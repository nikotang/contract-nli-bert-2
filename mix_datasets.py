import json
from sys import argv
from random import shuffle


def main():
    '''Give a list of arguments in command line. 
    Arguments should be paths and names to dataset files to be mixed. 
    The last argument should be the path and name of the new dataset file. 
    '''
    datasets = []

    for arg in argv[1:-1]:
        with open(arg, 'r') as f:
            dataset = json.load(f)
            datasets.append(dataset)

    mixed = {'documents': [], 'labels': {}}

    for dataset in datasets:
        mixed['documents'].extend(dataset['documents'])
        mixed['labels'].update(dataset['labels'])

    shuffle(mixed['documents'])

    with open(argv[-1], 'w') as outf:
        json.dump(mixed, outf)

if __name__ == "__main__":
    main()