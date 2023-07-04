"""
Wiki Finder

This Python script allows you to play the Wikipedia game by starting on one Wikipedia page and reaching another
page using only hyperlinks within the Wikipedia articles. The goal is to navigate from the start page to the
target page in the fewest number of clicks.
"""

import re
import urllib

import bs4
import numpy as np
import requests
import spacy

WIKIPEDIA_URL = "https://en.wikipedia.org"
START_PAGE = "Mathematics"
TARGET_PAGE = "Quantum_chromodynamics"

nlp = spacy.load("en_core_web_md")


def from_slug(article_title: str) -> str:
    return urllib.parse.unquote(article_title.replace("_", " "))


def get_article_text(article_title: str) -> str:
    url = f"{WIKIPEDIA_URL}/wiki/{article_title}"
    response = requests.get(url)
    return response.text


def get_article_links(html: str) -> set[str]:
    soup = bs4.BeautifulSoup(html, "html.parser")
    links = soup.select("#mw-content-text > div > p > a")
    article_links = set()

    for link in links:
        if (
            link.has_attr("href")
            and link["href"].startswith("/wiki/")
            and "#" not in link["href"]
            # and ":" not in link["href"]
        ):
            slug = link["href"].split("/")[-1]
            article_links.add(slug)

    return article_links


def get_link_ranking(current_article: str) -> float:
    link_text_doc = nlp(from_slug(current_article))
    target_page_doc = nlp(from_slug(TARGET_PAGE))

    similarity = link_text_doc.similarity(target_page_doc)

    return similarity


def find_next_article(current_article: str, already_visited: set[str]) -> str:
    text = get_article_text(current_article)
    links = get_article_links(text)

    link_rankings = {}

    for link in links:
        if link in already_visited:
            continue

        if link == TARGET_PAGE:
            return TARGET_PAGE

        link_rankings[link] = get_link_ranking(from_slug(link))

    similarities = np.array(list(link_rankings.values()))
    std = similarities.std()

    similarities += np.random.normal(0, std / 2, similarities.shape) * 0.1

    return list(link_rankings.keys())[np.argmax(similarities)]


if __name__ == "__main__":
    current_article = START_PAGE
    already_visited = {current_article}
    num_clicks = 0

    while current_article != TARGET_PAGE:
        print(f"{num_clicks} clicks: {current_article}")
        current_article = find_next_article(current_article, already_visited)
        already_visited.add(current_article)
        num_clicks += 1

    print(f"{num_clicks} clicks: {current_article}")
