from . import command, send

@command
def bots():
    """.bots - report info about bot"""
    send("Reporting in! [Python3]")
