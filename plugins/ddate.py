import gi
from gi.repository import GObject
gi.require_version('JiyuuBot', '1.0')
from gi.repository import JiyuuBot

import datetime
import calendar

class ddate(JiyuuBot.PluginsBasePlugin):
    def do_should_exec(self, msg):
        return msg.command('ddate')

    def do_exec(self, msg):
        dSeasons = ["Chaos", "Discord", "Confusion", "Bureaucracy", "The Aftermath"]
        dDays = ["Sweetmorn", "Boomtime", "Pungenday", "Prickle-Prickle", "Setting Orange"]
        year = int(datetime.datetime.now().strftime("%Y"))
        month = int(datetime.datetime.now().strftime("%m"))
        day = int(datetime.datetime.now().strftime("%d"))
        today = datetime.date(year, month, day)
        boolLeapYear = calendar.isleap(year)
        if boolLeapYear and month == 2 and day == 29:
            send("Today is St. Tib's Day, {} YOLD".format(year + 1166))
            return
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
        msg.send("Today is {}, the {} day of {} in the Year of Our Lady of Discord {}".format(dDays[dDayName], dDay, dSeasons[dSeason], year + 1166))
