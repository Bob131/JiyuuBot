from . import send, functions

@functions.command
def bots():
    """.bots - report info about bot"""
    send("Reporting in! [Python3]")
