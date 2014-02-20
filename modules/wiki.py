def wikipedia(self, string):
    import requests
    from urllib import parse
    UA = "JiyuuBot/1 (http://github.com/JiyuuProject/JiyuuBot; bob@bob131.so) BasedOnRequests/%s" % requests.__version__
    matches = re.findall("(\w+).wikipedia.org/wiki/([^\#\s\?]+)", string)
    for match in matches:
        match = (match[0], parse.unquote(match[1]))
        categories = requests.get("http://%s.wikipedia.org/w/api.php?action=query&prop=categories&format=json&cllimit=10&cldir=descending&titles=%s&redirects=" % match, headers={"user-agent": UA}).json()["query"]["pages"]
        categories = categories[list(categories.keys())[0]]
        if "missing" in categories.keys():
            self.conman.gen_send("Page not found")
        else:
            self.conman.gen_send("%s | Categories: %s" % (categories["title"], ", ".join(re.sub("\w+:", "", x["title"]) for x in categories["categories"])))

self._map("regex", ".*\w+.wikipedia.org/wiki/[^\#\s\?]+.*", wikipedia, "Wikipedia")
