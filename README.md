# Multitask Finetuning on ContractNLI

This is code for the paper [Natural Language Inference Transfer Learning in a Multi-Task Contract Dataset: In the Case of ContractNLI: a Document Information Extraction System](https://www.diva-portal.org/smash/record.jsf?pid=diva2:1801289). The code is a fork from [Span NLI BERT](https://github.com/stanfordnlp/contract-nli-bert/tree/main) by [Koreeda and Manning (2021)](https://stanfordnlp.github.io/contract-nli/). 

In short, Span NLI BERT is a strong baseline model for ContractNLI, a dataset of contracts labelled against common features formulated as NLI statements. This fork untangles the NLI classification and evidence identification tasks to finetune the model on [Adversarial NLI (ANLI)](https://aclanthology.org/2020.acl-main.441/) and [Contract Understanding Atticus Dataset (CUAD)](https://datasets-benchmarks-proceedings.neurips.cc/paper/2021/hash/6ea9ab1baa0efb9e19094440c317e21b-Abstract-round1.html) respectively.

Results show that fine-tuning on general domain NLI improves BERT-large model
performance for hypotheses that have a modest amount of both entailment and contradiction training examples, and that improving the model’s evidence identification
ability also lifts its NLI classification ability. Examples where the fine-tuned model
shows improvements in NLI classification indicate that additional general domain
NLI helps prompt the evidence identification task to retrieve a wider scope of text,
that is beneficial to capturing the semantic information for accurate NLI labelling.

ANLI and CUAD are reformatted to the ContractNLI format.

Below is the original readme.

---

# Span NLI BERT for ContractNLI

ContractNLI is a dataset for document-level natural language inference (NLI) on contracts whose goal is to automate/support a time-consuming procedure of contract review.
In this task, a system is given a set of hypotheses (such as "Some obligations of Agreement may survive termination.") and a contract, and it is asked to classify whether each hypothesis is _entailed by_, _contradicting to_ or _not mentioned by_ (neutral to) the contract as well as identifying _evidence_ for the decision as spans in the contract.
Please refer our paper in "Findings of EMNLP 2021" and [the dataset repository](https://stanfordnlp.github.io/contract-nli/) for the details of the task.

This repository maintains Span NLI BERT, a strong baseline for ContractNLI.
It (1) makes the problem of evidence identification easier by modeling the problem as multi-label classification over spans instead of trying to predict the start and end tokens, and (b) introduces more sophisticated context segmentation to deal with long documents.
We showed in our paper that Span NLI BERT significantly outperforms the existing models.

## Usage

### Dataset

Clone the repository to your desired directory.
Download the dataset from [the dataset repository](https://stanfordnlp.github.io/contract-nli/) and unzip JSON files to `./data/` directory (you may specify a custom dataset path by modifying a configuration file).

### Prerequisite

Set up a CUDA environment.
We used CUDA 11.1.1, cuDNN 8.0.5, NCCL 2.7.8-1 and GCC 7.4.0 in our experiments.

You need Python 3.8+ to run the codes.
We used Python 3.8.5 in our experiments.

Install requirements with Pip.

```bash
pip install -r requirements.txt
```

If you want to use A100 GPUs as we did in our experiments, you may need to install PyTorch manually (not reflected in `requirements.txt`).

```bash
pip install torch==1.8.1+cu111 torchvision==0.9.1+cu111 torchaudio==0.8.1 -f https://download.pytorch.org/whl/torch_stable.html
```

### Running experiments

You can run an experiment by feeding `train.py` an experiment configuration YAML file and specifying an output directory.

```bash
python train.py ./data/conf_base.yml ./output
```

## Reproducibility

We have tagged the implementations that we used for the experiments in our paper.
Please note that we have changed NLI label name since the experiments.
You may need to alter "Entailment" to "true", "Contradiction" to "false" and "NotMentioned" to "na" in the dataset JSON files, or apply commit `b0c4987` as a patch.

We carried out the experiments on [ABCI](abci.ai), a GPU cluster with a PBS-like job queue.
While it would not run in most users' environment, we provide our experiment procedure so that users can implement a similar procedure for their clusters.

```bash
# Generate configuration files in ./params
python gen_params.py data/param_tmpl.py 100 ./params

# Run tuning
./run_tuning.sh -s 1 -n 10 ${SECRET_GROUP_ID} ./params ./results

# Pick 3 models with the best validation macro NLI accuracies and report the average
python aggregate_results.py -n 3 -m macro_label_micro_doc.class.accuracy -o aggregated_metrics.txt ./results
```

## License

Our dataset is released under Apache 2.0.
Please refer attached "[LICENSE](./LICENSE)" for the exact terms.

This implementation has partially been derived from Huggingface's implementation of SQuAD BERT.
Please refer the commit log for the full changes.

When you use Span NLI BERT in your work, please cite our paper:

```bibtex
@inproceedings{koreeda-manning-2021-contractnli,
    title = "ContractNLI: A Dataset for Document-level Natural Language Inference for Contracts",
    author = "Koreeda, Yuta  and
      Manning, Christopher D.",
    booktitle = "Findings of the Association for Computational Linguistics: EMNLP 2021",
    year = "2021",
    publisher = "Association for Computational Linguistics"
}
```
