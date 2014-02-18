# ported from https://github.com/infinitylabs/UguuBot/blob/master/plugins/newegg.py

def format_item(self, item, show_url=True):
    """ takes a newegg API item object and returns a description """
    title = item["Title"]

    # format the rating nicely if it exists
    if not item["ReviewSummary"]["TotalReviews"] == "[]":
        rating = "Rated %s/5 (%s ratings)" % (item["ReviewSummary"]["Rating"], item["ReviewSummary"]["TotalReviews"][1:-1])
    else:
        rating = "No Ratings"

    if not item["FinalPrice"] ==  item["OriginalPrice"]:
        price = "{FinalPrice}, was {OriginalPrice}".format(**item)
    else:
        price = item["FinalPrice"]

    tags = []

    if item["Instock"]:
        tags.append("\x02Stock Available\x02")
    else:
        tags.append("\x02Out Of Stock\x02")

    if item["FreeShippingFlag"]:
        tags.append("\x02Free Shipping\x02")

    if item["IsFeaturedItem"]:
        tags.append("\x02Featured\x02")

    if item["IsShellShockerItem"]:
        tags.append("\x02SHELL SHOCKER®\x02")

    # join all the tags together in a comma seperated string ("tag1, tag2, tag3")
    tag_text = ", ".join(tags)

    if show_url:
        # create the item URL and shorten it
        return "\x02%s\x02 (%s) - %s - %s - %s" % (title, price, rating, tag_text, url)
    else:
        return "\x02%s\x02 (%s) - %s - %s" % (title, price, rating, tag_text)


def newegg_url(self, msg):
    matches = re.findall("/Product/Product\.aspx\?Item=([-_a-zA-Z0-9]+)", msg)
    import requests
    for match in matches:
        item = requests.get("http://www.ows.newegg.com/Products.egg/%s/ProductDetails" % match).json()
        self.conman.gen_send("%s" % self.run_func("newegg_format_item", item, show_url=False))


self.reg_func("newegg_format_item", format_item)
self._map("regex", ".*(www.newegg.com|newegg.com)/Product/Product\.aspx\?Item=([-_a-zA-Z0-9]+).*", newegg_url, "Newegg")
