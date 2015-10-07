#!/usr/bin/env python3

import re
import os
import math
import random
import textblob

random = random.SystemRandom()
chains = {}
sentence_starters = []

loaded = False


class SentenceLengthTracker:
    number_of_sentences = 0
    total_length = 0
    average = 0
    tokens = 0

    def __init__(self, ngrams):
        self.ngrams = ngrams

    def add(self, length):
        self.number_of_sentences += 1
        self.total_length += length
        self.average = self.total_length/self.number_of_sentences
        self.tokens = math.ceil(self.average/self.ngrams)


sentence_length_tracker = SentenceLengthTracker(10)


def load():
    with open(os.path.join(os.path.dirname(__file__), "g-dump.txt"), "r") as f:
        corpus = f.read()

    t = textblob.tokenizers.SentenceTokenizer()
    for line in corpus.split("\n"):
        if not line == "":
            for sentence in t.tokenize(line):
                sentence = sentence.lower()
                sentence = textblob.TextBlob(sentence)
                try:
                    first_word = sentence.ngrams(1)[0][0]
                    sentence_starters.append(first_word)
                except IndexError:
                    continue
                sentence_length_tracker.add(len(sentence.ngrams(1)))
                for ngram in sentence.ngrams(sentence_length_tracker.ngrams):
                    if not ngram[0] in chains:
                        chains[ngram[0]] = []
                    chains[ngram[0]].append(" ".join(ngram[1:]))

    global loaded
    loaded = True


def generate():
    assert(loaded)

    word = random.choice(sentence_starters)
    words = []
    for i in range(0, sentence_length_tracker.tokens):
        try:
            word = random.choice(chains[word])
        except KeyError:
            break
        words.append(word)
        word = word.split(" ")[-1]

    sentence = " ".join(words).capitalize() + "."
    if sentence == ".":
        return generate()
    return sentence


if __name__ == "__main__":
    import requests
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "dump":
        print("Fetching /g/ catalog...")
        pages = requests.get("http://a.4cdn.org/g/catalog.json").json()
        threads = []
        for page in pages:
            for thread in page["threads"]:
                threads.append(thread["no"])
        print("Found {} threads. Fetching...".format(len(threads)))
        posts = []

        for i in range(0, len(threads)):
            thread = threads[i]
            print("{}/{}".format(i, len(threads)), end="\r")
            _posts = requests.get("http://a.4cdn.org/g/thread/{}.json".format(thread)).json()
            for post in _posts["posts"]:
                if "com" in post:
                    post = post["com"].replace("<br>", "\n")
                    post = re.sub("<.+?>(.*?</.+?>)?", "", post)
                    post = re.sub("&.+?;", "", post)
                    posts.append(post)

        print("Done     ")
        print("Dumping to file...")
        with open("g-dump.txt", "a") as f:
            for post in posts:
                f.write(post)
                f.write("\n")

    else:
        load()
        for j in range(0, 5):
            print(generate())

else:
    from . import send, functions

    if os.path.exists(os.path.join(os.path.dirname(__file__), "g-dump.txt")):
        load()

    @functions.command
    def gmeme():
        print(__file__)
        send(generate() + " " + generate())
