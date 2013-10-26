def announce(self, command):
    import random
    global selected_intros
    filelist = os.listdir(os.path.join(MUSIC_PATH, NICK + "_intros"))
    filepath = ""
    while 1:
        if len(selected_intros) == len(filelist):
            selected_intros = []
        filepath = filelist[random.randint(0, len(filelist)-1)]
        filepath = os.path.join(NICK + "_intros", filepath)
        if not filepath in selected_intros:
            break
    selected_intros.append(filepath)
    self.conman.mpc.addid(filepath, 1)

selected_intros = []
self.map_command("announce", announce)
self.map_help("announce", ".announce - adds an intro track to the queue")
