from . import regex_handler, send


@regex_handler(".*DANCE.*")
def dancan():
    send("DANCES")
    send(":D-<")
    send(":D|-<")
    send(":D/-<")
    send(":D\-<")
