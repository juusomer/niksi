import markovify
import re
import itertools
import csv

def split_to_words(sentence):
    return re.split(r'\s+', sentence)

def split_to_sentences(niksi):
    return markovify.splitters.split_into_sentences(niksi)

def flatten(iterable_of_iterables):
    return list(itertools.chain.from_iterable(iterable_of_iterables))

def read_niksit(niksi_csv):
    return [row['contents'] for row in niksi_csv if row['contents']]

def build_model(niksit, state_size=2):
    # Corpus is a list of sentences represented as list of words
    sentences = flatten(map(split_to_sentences, niksit))
    corpus = list(map(split_to_words, sentences))

    generator = markovify.Text(
        input_text=None,
        state_size=state_size,
        parsed_sentences=corpus)

    return generator

def main():
    with open('niksit.csv') as f:
        niksi_csv = csv.DictReader(f)
        niksit = read_niksit(niksi_csv)

    model = build_model(niksit)

    with open('model.json', 'w+') as f:
        f.write(model.to_json())

if __name__ == '__main__':
    main()
