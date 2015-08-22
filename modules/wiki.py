import re
import urllib.parse
import requests
from . import functions, send

UA = "JiyuuBot/1 (http://github.com/Bob131/JiyuuBot; bob@bob131.so) BasedOnRequests/{}".format(requests.__version__)

@functions
def get_wiki_summary(title, lang='en'):
    summaries = requests.get("http://{}.wikipedia.org/w/api.php?action=query&prop=extracts&exintro=&explaintext=&format=json&cllimit=10&cldir=descending&titles={}&redirects=".format(lang, title), headers={"user-agent": UA}).json()["query"]["pages"]
    summaries = summaries[list(summaries.keys())[0]]
    if not "missing" in summaries.keys():
        if ":" in summaries["title"]:
            summaries["title"] = summaries["title"].split(":", 1)[-1]
            summaries["title"] = summaries["title"].split("/")[-1]
            summaries["title"] = re.sub("(?<=[a-z])(?=[A-Z])", " ", summaries["title"])
        try:
            if summaries["extract"] == "":
                raise KeyError
            return summaries["title"], re.split("(?<=[a-z]\.)\s+", summaries["extract"])[0].replace("\n", " ")
        except KeyError:
            return summaries["title"]


@functions.http_link_handler("(\w+).wikipedia.org/wiki/([^\#\s\?]+)")
def wikipedia(matches):
    for match in matches:
        match = (match[0], urllib.parse.unquote(match[1]))
        if not match[1].startswith("File:"):
            summary = functions.get_wiki_summary(match[1], match[0])
            if isinstance(summary, tuple):
                send("\x02{}\x02: {}".format(*summary))
            elif not summary == None:
                send("\x02{}\x02".format(summary))


@functions.command("w", "wiki")
def wikipedia(msginfo):
    """.wikipedia <query> - searches Wikipedia for a query"""
    query = " ".join(msginfo['msg'].split()[1:])
    try:
        searchresult = requests.get("https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={}&format=json&srprop=redirecttitle&srprop=snippet".format(query) , headers={"user-agent": UA}).json()['query']['search'][0]
    except IndexError:
        send("No results found")
        return
    title = searchresult['title']
    url = "https://en.wikipedia.org/wiki/{}".format(urllib.parse.quote(title))
    summary = functions.get_wiki_summary(title)
    if isinstance(summary, tuple):
        send("{} | {}".format(url, summary[1]))
    else:
        send(url)
