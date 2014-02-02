def ddate(self, command):
    import datetime
    import calendar
    dSeasons = ["Chaos", "Discord", "Confusion", "Beureacracy", "The Aftermath"]
    dDays = ["Sweetmorn", "Boomtime", "Pungenday", "Prickle-Prickle", "Setting Orange"]
    year = int(datetime.datetime.now().strftime("%Y"))
    month = int(datetime.datetime.now().strftime("%m"))
    day = int(datetime.datetime.now().strftime("%d"))
    today = datetime.date(year, month, day)
    boolLeapYear = calendar.isleap(year)
    if boolLeapYear and month ==2 and day == 29:
        self.conman.gen_send("Today is St. Tib's Day, %s YOLD" % year + 1166)
        return 0
    dayofYear = today.timetuple().tm_yday - 1
    if boolLeapYear and dayofYear >=60:
        dayofYear -= 1
    dSeason, dDay = divmod(dayofYear, 73)
    dDayName = day%5
    dDay += 1
    if 4 <= dDay <= 20 or 24 <= dDay <= 30:
        dDayOrdinal = "th"
    else:
        dDayOrdinal = ["st", "nd", "rd"][dDay % 10 - 1]
    self.conman.gen_send("Today is %s, the %s day of %s in the Year of Our Lady of Discord %d" % (dDays[dDayName], str(dDay) + dDayOrdinal, dSeasons[dSeason], year + 1166))


self._map("command", "ddate", ddate)
self._map("help", "ddate", ".ddate - Prints the current Discordian date")
