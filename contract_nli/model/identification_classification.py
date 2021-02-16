from dataclasses import dataclass
from typing import Optional

import torch
from torch import nn
from transformers.file_utils import ModelOutput
from transformers.models.bert import BertPreTrainedModel, BertModel
from transformers.utils import logging

from contract_nli.dataset.loader import NLILabel

logger = logging.get_logger(__name__)



@dataclass
class IdentificationClassificationModelOutput(ModelOutput):
    loss: Optional[torch.FloatTensor] = None
    loss_cls: Optional[torch.FloatTensor] = None
    loss_span: Optional[torch.FloatTensor] = None
    class_logits: torch.FloatTensor = None
    span_logits: torch.FloatTensor = None


class BertForIdentificationClassification(BertPreTrainedModel):

    IMPOSSIBLE_STRATEGIES = {'ignore', 'label', 'not_mentioned'}

    def __init__(self, config, impossible_strategy: str = 'ignore'):
        super().__init__(config)
        self.bert = BertModel(config, add_pooling_layer=True)
        self.class_outputs = nn.Linear(config.hidden_size, 3)
        self.span_outputs = nn.Linear(config.hidden_size, 2)
        self.dropout = nn.Dropout(config.hidden_dropout_prob)

        if impossible_strategy not in self.IMPOSSIBLE_STRATEGIES:
            raise ValueError(
                f'impossible_strategy must be one of {self.IMPOSSIBLE_STRATEGIES}')
        self.impossible_strategy = impossible_strategy

        self.init_weights()

    def forward(
        self,
        input_ids=None,
        attention_mask=None,
        token_type_ids=None,
        position_ids=None,
        head_mask=None,
        inputs_embeds=None,
        class_labels=None,
        span_labels=None,
        p_mask=None,
        is_impossible=None,
    ) -> IdentificationClassificationModelOutput:
        r"""
        span_mask (:obj:`torch.FloatTensor` of shape :obj:`(batch_size, sequence_length)`, `optional`):
            Mask to avoid performing loss calculation on non-target token indices.
            Mask values selected in [0, 1]: 1 for special [S] token that are not masked,
            0 for other normal tokens that are masked.
        span_labels (:obj:`torch.LongTensor` of shape :obj:`(batch_size,)`, `optional`):
            Labels for computing the sequence classification/regression loss. Indices should be in :obj:`[0, ...,
            config.num_labels - 1]`. If :obj:`config.num_labels == 1` a regression loss is computed (Mean-Square loss),
            If :obj:`config.num_labels > 1` a classification loss is computed (Cross-Entropy).

        """
        outputs = self.bert(
            input_ids,
            attention_mask=attention_mask,
            token_type_ids=token_type_ids,
            position_ids=position_ids,
            head_mask=head_mask,
            inputs_embeds=inputs_embeds,
            output_attentions=False,
            output_hidden_states=True,
            return_dict=True,
        )

        sequence_output = outputs.last_hidden_state
        pooled_output = outputs.pooler_output

        pooled_output = self.dropout(pooled_output)
        logits_cls = self.class_outputs(pooled_output)

        sequence_output = self.dropout(sequence_output)
        logits_span = self.span_outputs(sequence_output)

        if class_labels is not None:
            assert p_mask is not None
            assert span_labels is not None
            assert is_impossible is not None

            loss_fct = nn.CrossEntropyLoss()
            if self.impossible_strategy == 'ignore':
                class_labels = torch.where(
                    is_impossible == 0, class_labels,
                    torch.tensor(loss_fct.ignore_index).type_as(class_labels)
                )
            elif self.impossible_strategy == 'not_mentioned':
                class_labels = torch.where(
                    is_impossible == 0, class_labels, NLILabel.NOT_MENTIONED.value
                )
            loss_cls = loss_fct(logits_cls, class_labels)

            loss_fct = nn.CrossEntropyLoss()
            active_logits = logits_span.view(-1, 2)
            active_labels = torch.where(
                p_mask.view(-1) == 0, span_labels.view(-1),
                torch.tensor(loss_fct.ignore_index).type_as(span_labels)
            )
            loss_span = loss_fct(active_logits, active_labels)
            loss = loss_cls + loss_span
        else:
            loss, loss_cls, loss_span = None, None, None

        return IdentificationClassificationModelOutput(
            loss=loss,
            loss_cls=loss_cls,
            loss_span=loss_span,
            class_logits=logits_cls,
            span_logits=logits_span
        )