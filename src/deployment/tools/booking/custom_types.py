from typing import List
from pydantic import BaseModel
from enum import Enum
from datetime import datetime, date
from caldav import Event, Todo
from typing import Union
from dateutil import tz
try:
    from zoneinfo import ZoneInfo
except ImportError:
    from backports.zoneinfo import ZoneInfo
import tzlocal
from bs4 import BeautifulSoup as bs

class CreateBookingRequest(BaseModel):
    summary: str                # 日程标题，示例值："拜年"
    description: str = None     # 日程描述，示例值："与爸妈一起去叔叔家拜年"
    start_date: str = None
    start_time: str = None      # 日程开始时间，示例值："2018-09-01 14：00"
    end_date: str = None
    end_time: str = None        # 日程结束时间，示例值："2018-09-01 14：30"
    # location: str = None        # 日程地点信息，示例值："叔叔家"
    # people: str = None          # 日程涉及人员，示例值："和爸爸妈妈"
    remind: int = None          # 提前多久提醒日程开始，示例值："提前15分钟提醒"
    rrule: str = None           # RRULE:FREQ=WEEKLY;UNTIL=20241231T000000Z;BYDAY=MO

class GetBookingRequest(BaseModel):
    start_time: str
    end_time: str

class DeleteBookingRequest(BaseModel):
    uids: List[str]

class UpdateBookingRequest(BaseModel):
    uid: str
    start_date: str = None
    start_time: str = None
    end_date: str = None
    end_time: str = None
    summary: str = None
    remind: int = None
    description: str = None


class EventType(Enum):
    EVENT = 1
    TODO = 2

def parseTime(date_str, time_str: str) -> datetime:

    if date_str is None:
        date_str = str(date.today())

    if time_str is None:
        time_str = '00:00'

    date_time_str = f"{date_str} {time_str}"

    try:
        # Attempt to parse with seconds
        datetime_format = "%Y-%m-%d %H:%M:%S"
        datetime_obj = datetime.strptime(date_time_str, datetime_format).astimezone(ZoneInfo('UTC'))
    except ValueError:
        # If parsing with seconds fails, parse without seconds
        datetime_format = "%Y-%m-%d %H:%M"
        datetime_obj = datetime.strptime(date_time_str, datetime_format).astimezone(ZoneInfo('UTC'))
    return datetime_obj

def parseStartAndEndTime(start_date, start_time, end_date, end_time):
    if start_time is None and end_time is None:
        start_time = "00:00"
        end_time = "23:59"
    elif start_time is None:
        start_time = end_time
    elif end_time is None:
        end_time = start_time

    if start_date is None and end_date is None:
        start_date = end_date =  str(date.today())
    elif start_date is None:
        start_date = end_date
    elif end_date is None:
        end_date = start_date

    parsed_start_time = parseTime(start_date, start_time)
    parsed_end_time = parseTime(end_date, end_time)

    return (parsed_start_time, parsed_end_time)

class SearchCaldavEvent(BaseModel):
    start: datetime
    end: datetime = None
    event: bool = True
    expand: bool = False

    @staticmethod
    def fromSearchRequest(request: GetBookingRequest):
        start = datetime.strptime(request.start_time, "%Y-%m-%d %H:%M").astimezone(ZoneInfo('UTC'))
        end = datetime.strptime(request.end_time, "%Y-%m-%d %H:%M").astimezone(ZoneInfo('UTC'))
        return SearchCaldavEvent(start=start, end=end)

class CaldavEvent(BaseModel):
    summary: str = None
    rrule: dict = None
    dtstart: datetime = None
    dtend: datetime = None
    remind: int = None
    type: EventType = EventType.EVENT
    uid: str = None
    description: str = None

    def isEvent(self):
        return self.type == EventType.EVENT

    def isTODO(self):
        return self.type == EventType.TODO

    @staticmethod
    def fromUpdateRequest(request: UpdateBookingRequest):
        event = CaldavEvent(uid=request.uid)
        if request.start_time:
            event.dtstart = parseTime(request.start_date, request.start_time)
        if request.end_time:
            event.dtend = parseTime(request.end_date, request.end_time)
        if request.summary:
            event.summary = request.summary
        if request.description:
            event.description = request.description
        if request.remind:
            event.remind = request.remind
        return event

    @staticmethod
    def fromSearchResult(event_or_todo: Union[Event, Todo]):
        print(event_or_todo)
        xtype = EventType.EVENT if isinstance(event_or_todo, Event) else EventType.TODO
        ical = event_or_todo.icalendar_component
        def parse_time(dt):
            if isinstance(dt, datetime):
                return dt.astimezone()
            elif isinstance(dt, date):
                return datetime.fromordinal(dt.toordinal()).astimezone()
            return None
        try:
            return CaldavEvent(
                uid=str(ical['uid']),
                summary=str(ical['summary']),
                dtstart=parse_time(ical['dtstart'].dt),
                dtend=parse_time(ical['dtend'].dt),
                remind=int(ical.get('remind', 0)),
                type=xtype,
                description=str(ical.get('description', "")),
                rrule=dict(ical.get('rrule', {}))
            )
        except Exception as e:
            print(e, ical, ical['dtend'].dt, type(ical['dtend'].dt))


    @staticmethod
    def fromBookingRequest(request: CreateBookingRequest):
        dtstart, dtend = parseStartAndEndTime(request.start_date, request.start_time, request.end_date, request.end_time)

        if dtend <= datetime.now().astimezone(ZoneInfo('UTC')):
            raise Exception(f"Are you sure to create a passed event with end time: {dtend}?")

        if (not dtstart) and (not dtend):
            type = EventType.TODO
        else:
            type = EventType.EVENT

        rrule = dict(item.split("=") for item in request.rrule.split(";")) if request.rrule else None
        if rrule:
            for key, val in rrule.items():
                if key == 'UNTIL':
                    rrule[key] = datetime.strptime(val, "%Y%m%dT%H%M%SZ")
        return CaldavEvent(
                summary=request.summary,
                description=request.description,
                dtstart=dtstart,
                dtend=dtend,
                remind=request.remind,
                rrule=rrule,
                type=type)

    @staticmethod
    def fromGoogleEvent(event):
        def parse_google_time(gt):
            if 'dateTime' in gt:
                return datetime.fromisoformat(gt['dateTime'].rstrip('Z'))
            if 'date' in gt:
                return datetime.strptime(gt['date'], "%Y-%m-%d")

        def parse_rrule(rrule):
            if rrule and isinstance(rrule, list):
                rrule = rrule[0].split(':')[1]
                return dict(item.split("=") for item in rrule.split(";"))
            return {}

        def parse_reminders(reminders):
            if reminders is None:
                return None

            if 'overrides' in reminders:
                for reminder in reminders['overrides']:
                    return reminder['minutes']
            return None
        # print(event)
        return CaldavEvent(
            summary=event.get('summary', ""),
            dtstart=parse_google_time(event['start']),
            dtend=parse_google_time(event['end']),
            description=event.get('description', ""),
            rrule=parse_rrule(event.get('recurrence', None)),
            uid=event['iCalUID'],
            remind=parse_reminders(event.get('reminders', None)),
            type=EventType.EVENT
        )

    def toGoogleEvent(self):
        event = {}
        if self.summary:
            event['summary'] = self.summary
        if self.description:
            event['description'] = self.description
        if self.dtstart:
            event['start'] = {
                'dateTime': self.dtstart.isoformat(),
                'timeZone': tzlocal.get_localzone_name()
            }
        if self.dtend:
            event['end'] = {
                'dateTime': self.dtend.isoformat(),
                'timeZone': tzlocal.get_localzone_name()
            }
        if self.rrule:
            event['recurrence'] = [
                f'RRULE:{";".join([f"{key}={value}" for key, value in self.rrule.items()])}'
            ]
        if self.remind is not None:
            event['reminders'] = {
                'useDefault': False,
                'overrides': [
                    {'method': 'popup', 'minutes': self.remind},
                ],
            }
        print(event)
        return event
