import nltk 
import sys

TERMINALS = """
Adj -> "country" | "dreadful" | "enigmatical" | "little" | "moist" | "red"
Adv -> "down" | "here" | "never"
Conj -> "and" | "until"
Det -> "a" | "an" | "his" | "my" | "the"
N -> "armchair" | "companion" | "day" | "door" | "hand" | "he" | "himself"
N -> "holmes" | "home" | "i" | "mess" | "paint" | "palm" | "pipe" | "she"
N -> "smile" | "thursday" | "walk" | "we" | "word"
P -> "at" | "before" | "in" | "of" | "on" | "to"
V -> "arrived" | "came" | "chuckled" | "had" | "lit" | "said" | "sat"
V -> "smiled" | "tell" | "were"
"""

NONTERMINALS = """
S -> NP VP
NP -> Det N
NP -> Det Adj N
NP -> N
VP -> V
VP -> V NP
PP -> P NP
VP -> V NP PP
VP -> VP Conj VP
"""
# With this rule, we can generate sentences like:
# "Holmes arrived." or "He chuckled.", but more complex

# nltk for natural language processing.
grammar = nltk.CFG.fromstring(NONTERMINALS + TERMINALS)
parser = nltk.ChartParser(grammar)


def main():

    # If filename specified, read sentence from file
    if len(sys.argv) == 2:
        with open(sys.argv[1]) as f:
            s = f.read()

    # Otherwise, get sentence as input
    else:
        s = input("Sentence: ")

    # Convert input into list of words
    s = preprocess(s)

    # Attempt to parse sentence
    try:
        trees = list(parser.parse(s))
    except ValueError as e:
        print(e)
        return
    if not trees:
        print("Could not parse sentence.")
        return

    # Print each tree with noun phrase chunks
    for tree in trees:
        tree.pretty_print()

        print("Noun Phrase Chunks")
        for np in np_chunk(tree):
            print(" ".join(np.flatten()))


def preprocess(sentence):
    """
    Convert `sentence` to a list of its words.
    Pre-process sentence by converting all characters to lowercase
    and removing any word that does not contain at least one alphabetic
    character.
    """
    # Convert to lowercase
    sentence = sentence.lower()

    # Split the sentence into words for our list (every blank space will be a split in our sentence)
    words = sentence.split()

    # Create list of words
    result = []

    for word in words:
        # We will delete all characters that aren't letters, for that we loop through each word
        # Cleaned word will contain all the letters of the word without punctuation marks
        cleaned_word = ''.join(char for char in word if char.isalpha())

        if cleaned_word: # if it exists add to list
            result.append(cleaned_word)

    return result

def np_chunk(tree):
    """
    Return a list of all noun phrase chunks in the sentence tree.
    A noun phrase chunk is defined as any subtree of the sentence
    whose label is "NP" that does not itself contain any other
    noun phrases as subtrees.
    """
    noun_phrases = []

    # De todos los subárboles t, solo quiero los que tengan la etiqueta "NP"
    for subtree in tree.subtrees(filter=lambda t: t.label() == "NP"):

        #Check if noun phrase contains another np inside it (we want the smallest)
        # subtree.subtrees(lambda t: t != subtree): recorre todos los subárboles dentro de subtree, excepto el propio subtree
        if not any(sub.label() == "NP" for sub in subtree.subtrees(lambda t: t != subtree)):
            noun_phrases.append(subtree)

    return noun_phrases


if __name__ == "__main__":
    main()
