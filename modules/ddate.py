@self.command(help="Prints the current Discordian date")
def ddate(self, msginfo):
    import datetime
    import calendar
    dSeasons = ["Chaos", "Discord", "Confusion", "Beureacracy", "The Aftermath"]
    dDays = ["Sweetmorn", "Boomtime", "Pungenday", "Prickle-Prickle", "Setting Orange"]
    year = int(datetime.datetime.now().strftime("%Y"))
    month = int(datetime.datetime.now().strftime("%m"))
    day = int(datetime.datetime.now().strftime("%d"))
    today = datetime.date(year, month, day)
    boolLeapYear = calendar.isleap(year)
    if boolLeapYear and month == 2 and day == 29:
        self.conman.gen_send("Today is St. Tib's Day, %s YOLD" % year + 1166, msginfo)
        return 0
    dayofYear = today.timetuple().tm_yday - 1
    if boolLeapYear and dayofYear >=60:
        dayofYear -= 1
    dSeason, dDay = divmod(dayofYear, 73)
    dDayName = (dayofYear)%5
    dDay += 1
    if 10 <= dDay % 100 < 20:
        dDay = str(dDay) + 'th'
    else:
       	dDay = str(dDay) + {1 : 'st', 2 : 'nd', 3 : 'rd'}.get(dDay % 10, "th")
    self.conman.gen_send("Today is %s, the %s day of %s in the Year of Our Lady of Discord %d" % (dDays[dDayName], dDay, dSeasons[dSeason], year + 1166), msginfo)
