import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def transition_model_test():

    expected = {"1.html": 0.05, "2.html": 0.475, "3.html": 0.475}
    result = transition_model({"1.html": {"2.html", "3.html"}, "2.html": {"3.html"}, "3.html": {"2.html"}}, "1.html", .85)
    print(f"Result = {result}")
    print(f"Expected = {expected}")
    valid = result == expected
    print(f"PASS: {valid}")


def main():
    # test_case()
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

    N = len(corpus)

    # If page has no outgoing links, then transition_model should return a probability distribution that
    # chooses randomly among all pages with equal probability.
    if len(corpus[page]) == 0:
        return {page_name: 1 / N for page_name in corpus}

    # With probability 1 - d, the surfer chose a page at random and ended up on page p.
    result = { page_name:  (1 - damping_factor) / N for page_name in corpus}

    # With probability d, the surfer followed a link from a page i to page p.
    for page_name in corpus[page]:
        result[page_name] += damping_factor / len(corpus[page])

    return result


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """

    # initialize the results dictionary
    result = {page_name: 0 for page_name in corpus}

    # The  first sample should be generated by choosing from a page at random.
    current_page = random.choice(list(corpus.keys()))

    for i in range(0, n):

        trans_model = transition_model(corpus, current_page, damping_factor)

        # add the probabilities to the results and average them out
        for page_name in trans_model:
            result[page_name] += trans_model[page_name]

        # For each of the remaining samples,the next sample should be generated from the previous sample transition
        # model probabilities. Use the weighted responses to choose the next current_page with some help from the
        # python random choices function
        current_page = random.choices(list(trans_model.keys()), weights=list(trans_model.values()), k=1).pop()

    result = { k: v / n for k, v in result.items() }

    return result


def page_rank(corpus, damping_factor, N, page_ranks):
    """
    Calculate the PageRank on the Corpus pages

    Formula ...
    PR(p) = (1 - d / N) + d * SUM(0..i) { PR(i) / NumLinks(i) }
    d is the damping factor
    N is the total number of pages in the corpus,
    i ranges over all pages that link to page p
    NumLinks(i) is the number of links present on page i.
    """
    results = {}

    # PR(p)
    for page_name in corpus:
        sum_of_links = 0

        # SUM(0..i) { PR(i) / NumLinks(i)
        for i in corpus:
            linked_pages = corpus[i]
            num_links = len(corpus[i])

            # calculating a page’s PageRank based on the PageRanks of all pages that link to it
            # PR(i) / NumLinks(i)
            if page_name in linked_pages:  # link to page_name?
                sum_of_links += page_ranks[i] / num_links

            # A page that has no links at all should be interpreted as having one link for every page in the corpus
            # PR(i) / N
            if num_links == 0:  # no links?
                sum_of_links += page_ranks[i] / N

        # PR(p) = (1 - d / N) + d * SUM(0..i) { PR(i) / NumLinks(i) }
        PR = ((1 - damping_factor) / N) + (damping_factor * sum_of_links)
        results[page_name] = PR

    return results


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """

    converge_at = 0.001
    converged = False
    N = len(corpus)

    # start by assuming the PageRank of every page is 1 / N
    page_ranks = {page_name: 1 / N for page_name in corpus}

    while not converged:

        results = page_rank(corpus, damping_factor, N, page_ranks)

        max_diff = 1.0

        for page_name, probability in results.items():
            rank_change = abs(results[page_name] - page_ranks[page_name])
            max_diff = max(rank_change, converge_at)
            page_ranks[page_name] = probability

        # have we converged?
        converged = max_diff <= converge_at

    return page_ranks


if __name__ == "__main__":
    main()
