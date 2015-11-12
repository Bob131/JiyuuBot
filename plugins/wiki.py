import gi
from gi.repository import GObject
gi.require_version('JiyuuBot', '1.0')
from gi.repository import JiyuuBot

import re
import urllib.parse
import requests


class wiki_base:
    UA = "{}BasedOnRequests/{}".format(JiyuuBot.UA, requests.__version__)

    def get_wiki_summary(self, title, lang='en'):
        summaries = requests.get("http://{}.wikipedia.org/w/api.php?action=query&prop=extracts&exintro=&explaintext=&format=json&cllimit=10&cldir=descending&titles={}&redirects=".format(lang, title), headers={"user-agent": self.UA}).json()["query"]["pages"]
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


class wiki_regex(JiyuuBot.PluginsBasePlugin, wiki_base):
    regex = "(\w+).wikipedia.org/wiki/([^\#\s\?]+)"

    def do_should_exec(self, msg):
        return msg.regex(self.regex, False)

    def do_exec(self, msg):
        for match in re.findall(self.regex, msg.get_text(), re.IGNORECASE):
            match = (match[0], urllib.parse.unquote(match[1]))
            if not match[1].startswith("File:"):
                summary = self.get_wiki_summary(match[1], match[0])
                if isinstance(summary, tuple):
                    msg.send("\x02{}\x02: {}".format(*summary))
                elif not summary == None:
                    msg.send("\x02{}\x02".format(summary))


class wiki_cmd(JiyuuBot.PluginsBasePlugin, wiki_base):
    def do_activate(self, help, _):
        help.add('wikipedia', 'search Wikipedia for supplied search term')

    def do_should_exec(self, msg):
        return msg.command('w') or msg.command('wiki') or msg.command('wikipedia')

    def do_exec(self, msg):
        args = msg.get_args()
        query = " ".join(args)
        try:
            searchresult = requests.get("https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={}&format=json&srprop=redirecttitle&srprop=snippet".format(query) , headers={"user-agent": self.UA}).json()['query']['search'][0]
        except IndexError:
            msg.send("No results found")
            return
        title = searchresult['title']
        url = "https://en.wikipedia.org/wiki/{}".format(urllib.parse.quote(title))
        summary = self.get_wiki_summary(title)
        if isinstance(summary, tuple):
            msg.send("{} | {}".format(url, summary[1]))
        else:
            msg.send(url)
