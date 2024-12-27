import json
import ast
from typing import Type, Any, Optional, List, Dict
from pydantic import BaseModel, Field, Extra
import os
import sys
import traceback

PROJECT_DIR = os.path.join(os.path.dirname(__file__), '../../../..')
sys.path.append(PROJECT_DIR)

from src.deployment.tools.booking.custom_types import CreateBookingRequest, DeleteBookingRequest, UpdateBookingRequest, GetBookingRequest
from src.deployment.tools.booking.custom_calendar import create_booking, delete_bookings, update_booking, get_bookings, reset_calendar
from datetime import datetime

class BookingToolBase:
    pass

class MyBaseModel(BaseModel):
    class Config:
        @staticmethod
        def schema_extra(schema: Dict[str, Any], model: Type['MyBaseModel']) -> None:
            for prop in schema.get('properties', {}).values():
                prop.pop('title', None)
            schema.pop('title', None)

class CreateBookingInput(MyBaseModel):
    summary: str = Field(description="Provides a brief title for the event, for instance, 'New Year Visit'.")
    start_date: str = Field(description="Indicates the event's start date in YYYY-MM-DD format, e.g., '2024-02-01'.", default=None)
    start_time: str = Field(description="Indicates the event's start time in HH:MM format, such as '14:00'.", default=None)
    end_date: str = Field(description="Indicates the event's end date in YYYY-MM-DD format, e.g., '2024-02-01'.", default=None)
    end_time: str = Field(description="Denotes the event's end time in HH:MM format, e.g., '16:00'.", default=None)
    description: str = Field(description="Gives a detailed description of the event, like 'Visiting uncle's house with parents for New Year greetings'.", default=None)
    # location: str = Field(description="The venue of the event, for example, 'Uncle's House'.", default=None)
    # people: str = Field(description="Lists the people involved in the event, such as 'Dad, Mom'.", default=None)
    remind: int = Field(description="The number of minutes before the event starts when a reminder should be sent, e.g., 15. This is an optional parameter; if the user does not mention it, the reminder parameter should not be included. Do not fill in this parameter arbitrarily.", default=None)
    rrule: str = Field(description="Recurring rule following the iCalendar (RFC 5545) standard, for example, 'FREQ=WEEKLY;UNTIL=20241231T000000Z;BYDAY=MO'.", default=None)

class CreateBooking(BookingToolBase):
    name = "create_booking"
    description = "Creates an event on the current user's calendar for appointments, meetings, or other types of events. If the user does not provide a title, they should be prompted again to ensure completeness. If the user specifies vague times like 'morning' or 'forenoon', these should be mapped to specific times later than the current time, e.g., midnight defaults to 1 AM, morning to 7 AM, and forenoon to 10 AM."

    args_schema: Type[MyBaseModel] = CreateBookingInput
    def _run(self, summary, start_date=None, start_time=None, end_date=None, end_time=None, description=None, remind=None, rrule=None):
        try:
            create_booking_Request = CreateBookingRequest(
                summary=summary,
                start_date=start_date,
                start_time=start_time,
                end_date=end_date,
                end_time=end_time,
                description=description,
                # location=location,
                # people=people,
                remind=remind,
                rrule=rrule
            )
            event = create_booking(create_booking_Request)
            return {"status":"ok", "event_created": event}

        except Exception as exp:
            print(traceback.format_exc())
            return {"status": "failed", "reason": str(exp)}

class GetBookingsInput(MyBaseModel):
    start_time: str = Field(description="Specifies the start time of the querying range in 'YYYY-MM-DD HH:MM' format, for instance, '2024-02-26 00:00'.")
    end_time: str = Field(description="Specifies the end time of the querying range in 'YYYY-MM-DD HH:MM' format, such as '2024-02-26 23:59'.")

class GetBookings(BookingToolBase):
    name = "get_bookings"
    description = "Retrieves events scheduled on the current user's calendar within a specified date range. The user needs to provide at least one piece of information as a parameter. If no parameters are provided, ask the user for more information to proceed with the search operation."
    args_schema: Type[MyBaseModel] = GetBookingsInput
    def _run(self, start_time, end_time):
        try:
            get_bookings_request = GetBookingRequest(start_time=start_time, end_time=end_time)
            events = get_bookings(get_bookings_request)
            # events_tup = ast.literal_eval(str(events))
            # decoded_events = [json.loads(event) for event in events_tup[0]]
            return {"status": "ok", "events": events}
        except Exception as exp:
            print(traceback.format_exc())
            return {"status": "failed", "reason": str(exp)}


class DeleteBookingInput(MyBaseModel):
    uids: List[str] = Field(description="A list of unique identifiers (UIDs) for the events to be deleted.")

class DeleteBookings(BookingToolBase):
    name = "delete_bookings"
    description = """Deletes specified events using their unique identifiers (UIDs). To delete events, first retrieve their UIDs by calling the get_bookings function. If the provided information uniquely identifies an event, then delete that event. If multiple events match the criteria, ask the user whether to delete 'all' or a specific event."""
    args_schema: Type[MyBaseModel] = DeleteBookingInput
    def _run(self, uids):
        try:
            delete_booking_request = DeleteBookingRequest(uids=uids)
            deleted_events = delete_bookings(delete_booking_request)
            if len(deleted_events) == 0:
                return {"status": "failed", "reason": "no events deleted."}
            return {"status": "ok", "events_deleted": deleted_events}
        except Exception as exp:
            print(traceback.format_exc())
            return {"status": "failed", "reason": str(exp)}


class UpdateBookingInput(MyBaseModel):
    uid: str = Field(description="The unique identifier (UID) of the event to be updated, which can be retrieved using `get_bookings`.")
    start_date: str = Field(description="The updated start date of the event in YYYY-MM-DD format, e.g., '2024-02-01'.", default=None)
    start_time: str = Field(description="The updated start time of the event in HH:MM format, for example, '00:00'.", default=None)
    end_date: str = Field(description="The updated end date of the event in YYYY-MM-DD format, e.g., '2024-02-01'.", default=None)
    end_time: str = Field(description="The updated end time of the event in 'HH:MM' format, e.g., '23:59'.", default=None)
    summary: str = Field(description="The updated summary or title of the event.", default=None)
    description: str = Field(description="The updated detailed description of the event.", default=None)

class UpdateBooking(BookingToolBase):
    name = "update_booking"
    description = "Updates an existing event using its unique identifier (UID). Ensure to retrieve the UID through get_bookings before attempting an update. If the input information uniquely identifies an event, proceed with the update; if multiple events match the criteria, ask the user whether to update 'all' or a specific event."
    args_schema: Type[MyBaseModel] = UpdateBookingInput
    def _run(self, uid, start_date=None, start_time=None, end_date=None, end_time=None, summary=None, description=None, remind=None):
        try:
            update_booking_request = UpdateBookingRequest(
                uid=uid,
                start_date=start_date,
                start_time=start_time,
                end_date=end_date,
                end_time=end_time,
                summary=summary,
                description=description,
                remind=remind
            )

            event = update_booking(update_booking_request)
            return {"status": "ok", "event": event}
        except Exception as exp:
            print(traceback.format_exc())
            return {"status": "failed", "reason": str(exp)}

class ResetCalendar(BookingToolBase):
    name = "reset_calendar"
    def _run(self):
        try:
            reset_calendar()
            return {"status": "ok"}
        except Exception as exp:
            print(traceback.format_exc())
            return {"status": "failed", "reason": str(exp)}


if __name__ == "__main__":
    get_booking_tool = GetBookings()
    out = get_booking_tool._run(datetime(2026, 1, 1, 1).strftime("%Y-%m-%d %H:%M"), datetime(2026, 3, 28, 22, 30).strftime("%Y-%m-%d %H:%M"))
    # print(json.dumps(out, ensure_ascii=False, indent=4))
    print(out)

    # update_booking_tool = UpdateBooking()
    # print(update_booking_tool._run(uid='3a652edb-e1ff-11ee-9190-e865382dd746', summary='跑跑', remind=30))

    # delete_booking_tool = DeleteBookings()
    # print(delete_booking_tool._run(['29e85e5c-e1ee-11ee-8cf0-e865382dd746']))
    #
    create_booking_tool = CreateBooking()
    out = create_booking_tool._run(
        start_date='2003-02-28',
        start_time='06:30',
        summary='晨跑', description="每天早上跑步锻炼",
        end_date = "2033-02-28",
        end_time="07:30",
        # rrule="FREQ=DAILY;INTERVAL=1"
    )
    # args = {
    #     "description": "家庭游戏夜",
    #     "end_date": "2027-01-01",
    #     "end_time": "21:00",
    #     "rrule": "FREQ=MONTHLY;BYDAY=1WE;UNTIL=20251231T000000Z",
    #     "start_date": "2026-01-01",
    #     "start_time": "18:00",
    #     "summary": "家庭游戏夜"
    # }
    # out = create_booking_tool._run(**args)
    print(out)