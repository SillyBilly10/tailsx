from src.helpers import makeHTMLRequest, latest_commit
from urllib.parse import unquote
from _config import *
from flask import request, render_template, jsonify, Response
import time
from urllib.parse import quote
import base64


def imageResults(query) -> Response:
    # remember time we started
    start_time = time.time()

    api = request.args.get("api", "false")

    # grab & format webpage
    soup = makeHTMLRequest(f"https://lite.qwant.com/?q={query}&t=images")

    # get 'img' ellements
    ellements = soup.findAll("div", {"class": "images-container"})
    # get source urls
    image_sources = [a.find('img')['src'] for a in ellements[0].findAll('a') if a.find('img')]

    # get alt tags
    image_alts = [img['alt'] for img in ellements[0].findAll('img', alt=True)]

    # generate results
    images = [f"/img_proxy?url={quote(img_src)}" for img_src in image_sources]

    # decode urls
    links = [a['href'] for a in ellements[0].findAll('a') if a.has_attr('href')]
    links = [url.split("?position")[0].split("==/")[-1] for url in links]
    links = [unquote(base64.b64decode(link).decode('utf-8')) for link in links]

    # list
    results = []
    for image, link, image_alt in zip(images, links, image_alts):
        results.append((image, link, image_alt))

    # calc. time spent
    end_time = time.time()
    elapsed_time = end_time - start_time

    # render
    if api == "true" and API_ENABLED == True:
        # return the results list as a JSON response
        return jsonify(results)
    else:
        return render_template("images.html", results=results, title=f"{query} - TailsX",
            q=f"{query}", fetched=f"Fetched the results in {elapsed_time:.2f} seconds",
            theme=request.cookies.get('theme', DEFAULT_THEME), DEFAULT_THEME=DEFAULT_THEME,
            javascript=request.cookies.get('javascript', 'enabled'), type="image",
            new_tab=request.cookies.get("new_tab"), repo_url=REPO, API_ENABLED=API_ENABLED,
            TORRENTSEARCH_ENABLED=TORRENTSEARCH_ENABLED, commit=latest_commit())
