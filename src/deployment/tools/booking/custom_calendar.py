import caldav
import os
import sys

PROJECT_DIR = os.path.join(os.path.dirname(__file__), '../../../..')
sys.path.append(PROJECT_DIR)

from src.deployment.tools.booking.custom_types import CaldavEvent, SearchCaldavEvent

calendar = None

caldav_client = caldav.DAVClient(
    url='http://baikal.mtc.sensetime.com/dav.php',
    username='test',
    password='test@sensetime.com',
    headers={"WWW-Authenticate": "digest"},
)

def get_default_calendar():
    global calendar
    if calendar:
        return calendar
    my_principal = caldav_client.principal()
    try:
        default_calendar = my_principal.calendar(name='Default calendar')
    except:
        my_principal.make_calendar(name="Default calendar")
        default_calendar = my_principal.calendar(name='Default calendar')

    calendar = default_calendar
    return calendar

def reset_calendar():
    calendar = get_default_calendar()
    events = calendar.events()
    if len(events) < 100:
        return

    for event in events:
        event.delete()
    print('[+] delete calendar all events')

def create_booking(args):
    calendar = get_default_calendar()
    caldav_event = CaldavEvent.fromBookingRequest(args)

    if caldav_event.isEvent():
        saved_event = calendar.save_event(**caldav_event.dict())
    elif caldav_event.isTODO():
        saved_event = calendar.save_todo(**caldav_event.dict())
    return {"status":"ok", "uid": str(saved_event.icalendar_component.get("uid"))}, 200

def delete_bookings(args):
    calendar = get_default_calendar()
    uid_strs = []
    for uid in args.uids:
        event = calendar.event_by_uid(uid)
        event.delete()
        uid_strs.append(str(event.icalendar_component.get("uid")))
    return {"status": "ok", "uid": uid_strs}, 200

def get_bookings(args):
    calendar = get_default_calendar()
    search_event = SearchCaldavEvent.fromSearchRequest(args)
    events_fetched = calendar.search(**search_event.dict())
    events = []
    for event in events_fetched:
        events.append(CaldavEvent.fromSearchResult(event))
    return events, 200

def update_booking(args):
    calendar = get_default_calendar()
    event = calendar.event_by_uid(args.uid)
    if not event:
        return {"status": "failed", "reason": f"event with uid: {args.uid} not found"}, 500
    updated_caldav_event = CaldavEvent.fromUpdateRequest(args)
    ical = event.icalendar_component
    if updated_caldav_event.dtstart:
        ical['dtstart'].dt = updated_caldav_event.dtstart
    if updated_caldav_event.dtend:
        ical['dtend'].dt = updated_caldav_event.dtend
    if updated_caldav_event.summary:
        ical['summary'] = updated_caldav_event.summary
    if updated_caldav_event.description:
        ical['description'] = updated_caldav_event.description
    if updated_caldav_event.remind:
        ical['remind'] = updated_caldav_event.remind
    event.save()
    return CaldavEvent.fromSearchResult(event).json(ensure_ascii=False), 200
