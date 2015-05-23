@self.regex(".*\w+.wikipedia.org/wiki/[^\#\s\?>]+.*")
def wikipedia(self, msginfo):
	import requests
	from urllib import parse
	UA = "JiyuuBot/1 (http://github.com/JiyuuProject/JiyuuBot; bob@bob131.so) BasedOnRequests/%s" % requests.__version__
	matches = re.findall("(\w+).wikipedia.org/wiki/([^\#\s\?]+)", msginfo["msg"])
	for match in matches:
		match = (match[0], parse.unquote(match[1]))
		if not match[1].startswith("File:"):
			summaries = requests.get("http://%s.wikipedia.org/w/api.php?action=query&prop=extracts&exintro=&explaintext=&format=json&cllimit=10&cldir=descending&titles=%s&redirects=" % match, headers={"user-agent": UA}).json()["query"]["pages"]
			summaries = summaries[list(summaries.keys())[0]]
			if "missing" in summaries.keys():
				self.conman.gen_send("Page not found", msginfo)
			else:
				summary = summaries["extract"].split('\n')[0]
				self.conman.gen_send("%s | Summary: %s" % (summaries["title"],  summary), msginfo)