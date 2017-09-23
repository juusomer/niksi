import re
import csv
import markovify
from itertools import chain
from operator import itemgetter

def split_to_words(sentence):
    return re.split(r'\s+', sentence)

def split_to_sentences(niksi):
    return markovify.splitters.split_into_sentences(niksi)

def flatten(iterable_of_iterables):
    return chain.from_iterable(iterable_of_iterables)

def read_niksit(niksi_csv):
    return map(itemgetter('content'), niksi_csv)

def build_model(niksit, state_size=2):
    sentences = flatten(map(split_to_sentences, niksit))
    parsed_sentences = list(map(split_to_words, sentences))
    return markovify.Text(
        input_text=None,
        state_size=state_size,
        parsed_sentences=parsed_sentences)

def main():
    with open('niksit.csv') as f:
        niksi_csv = csv.DictReader(f)
        niksit = read_niksit(niksi_csv)
        model = build_model(niksit)

    with open('model.json', 'w+') as f:
        f.write(model.to_json())

if __name__ == '__main__':
    main()
