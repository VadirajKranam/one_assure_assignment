import requests
from datetime import datetime, timedelta, time
from app import scheduler
import pytz
from app.models import User,Meeting

def send_post_request(url, data):
    response = requests.post(url, json=data)
    return response.json()

def is_within_dnd(dnd_start, dnd_end, notify_time):
    notify_time = notify_time.time()
    dnd_start = datetime.strptime(dnd_start, '%H:%M').time()
    dnd_end = datetime.strptime(dnd_end, '%H:%M').time()

    if dnd_start < dnd_end:
        return dnd_start <= notify_time <= dnd_end
    else:  
        return notify_time >= dnd_start or notify_time <= dnd_end

def schedule_notification(meeting_id, user, start_time, timezone):
    user_timezone = pytz.timezone(user.preferred_timezone)
    meeting_timezone = pytz.timezone(timezone)
    
    start_time_utc = meeting_timezone.localize(start_time).astimezone(pytz.utc)
    notify_time_utc = start_time_utc - timedelta(hours=1)
    notify_time_user_tz = notify_time_utc.astimezone(user_timezone)

    if is_within_dnd(user.dnd_start_time, user.dnd_end_time, notify_time_user_tz):
        print(f"Notification time {notify_time_user_tz} falls within DND period for user {user.name}. Notification not scheduled.")
        return

    scheduler.add_job(
        func=send_post_request,
        trigger='date',
        run_date=notify_time_utc,
        args=["https://example.com/notify", {'meeting_id': meeting_id, 'user_id': user.id}]
    )
    print(f"Notification scheduled for {notify_time_user_tz} for user {user.name}.")
    
def is_available(participant,meeting):
    for booked_slot in participant.meetings:
        tz=pytz.timezone(participant.preferred_timezone)
        dt1 = tz.localize(meeting.start_time)
        dt2 = tz.localize(booked_slot.start_time)
        dt1_converted = dt1.astimezone(pytz.utc)
        bt1=tz.localize(meeting.end_time)
        bt2=tz.localize(booked_slot.end_time)
        bt1_converted=bt1.astimezone(pytz.utc)
        # print(participant.name,"meeting start in utc :  ",dt1_converted,"meeting end in utc",bt1_converted,end=" ")
        # print("booked start in utc: ",dt2_converted,"booked end in utc: ",bt2_converted)
        if(dt1_converted>=dt2 and bt1_converted<=bt2):
            return False
    return True
            
def get_booked_slots(user,start_time,end_time):
    meetings=Meeting.objects(
        participants=user.id,
        start_time__gte=start_time,
        start_time__lte=end_time    
    )
    booked_slots=[]
    for meeting in meetings:
        is_same_timezone=True if user.preferred_timezone==meeting.timezone else False
        if not is_same_timezone:
            tz=pytz.timezone(user.preferred_timezone)
            dt1=meeting.start_time.astimezone(tz).replace(tzinfo=None)
            bt1=meeting.end_time.astimezone(tz).replace(tzinfo=None)
            booked_slots.append({"start_time":dt1,"end_time":bt1,"time_zone":user.preferred_timezone,"meeting_type":meeting.meeting_type})
        else:
            booked_slots.append({"start_time":meeting.start_time,"end_time":meeting.end_time,"time_zone":user.preferred_timezone,"meeting_type":meeting.meeting_type})
    return booked_slots

def get_free_time_slots(start_time,end_time,booked_slots):
    free_slots=[]
    current_time = start_time
    for meeting in booked_slots:
        print(current_time," ",meeting["start_time"])
        if current_time < meeting["start_time"]:
            free_slots.append({"start_time":current_time,"end_time" :meeting["start_time"],"duration":(meeting["start_time"]-current_time).total_seconds()/60})
            current_time = meeting["end_time"]
            
    if current_time < end_time:
            free_slots.append({"start_time":current_time,"end_time" :end_time,"duration":(end_time-current_time).total_seconds()/60})
    return free_slots

        


            
                
            
    

