import os
import random
import re
import sys

DAMPING = 0.85 # represents the damping factor 
SAMPLES = 10000 # number of samples we’ll use to estimate PageRank using the sampling method


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory): 
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    n = len(corpus) # n es la longitud del diccionario corpus que incluye todas las paginas/enlaces
    prob = dict()

    # If the page has no outgoing links, it links to all pages equally
    links = corpus[page]
    if not links:
        for p in corpus:
            prob[p] = 1 / n
        return prob

    # Otherwise, apply damping formula
    for p in corpus:
        prob[p] = (1 - damping_factor) / n
        if p in links:
            prob[p] += damping_factor / len(links)

    return prob
    


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    pages = list(corpus.keys()) # crea una lista que contiene todos los nombres de las páginas

    # Start from a random page
    current_page = random.choice(pages)

    # Initialize visit counts
    counts = {page: 0 for page in pages}

    for i in range(n):
        counts[current_page] += 1
        model = transition_model(corpus, current_page, damping_factor)
        current_page = random.choices(
            population=list(model.keys()),
            weights=list(model.values()),
            k=1
        )[0]

    # Convert counts to probabilities
    pagerank = {page: counts[page] / n for page in pages}
    return pagerank


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    N = len(corpus)
    pagerank = {page: 1 / N for page in corpus}

    # Handle dangling links (pages with no outgoing links)
    links = {p: (corpus[p] if corpus[p] else set(corpus.keys())) for p in corpus}

    converged = False
    while not converged:
        new_rank = {}
        for page in corpus:
            total = 0
            for possible_page in corpus:
                if page in links[possible_page]:
                    total += pagerank[possible_page] / len(links[possible_page])
            new_rank[page] = (1 - damping_factor) / N + damping_factor * total

        # Check for convergence
        converged = all(abs(new_rank[p] - pagerank[p]) < 0.001 for p in corpus)
        pagerank = new_rank

    # Normalize (ensure sum = 1)
    total_sum = sum(pagerank.values())
    pagerank = {p: v / total_sum for p, v in pagerank.items()}
    return pagerank


if __name__ == "__main__":
    main()
