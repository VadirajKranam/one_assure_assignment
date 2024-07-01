from flask import Blueprint, request, jsonify
from datetime import datetime
from app.main import bp
from app.models import User,Meeting,NotificationInterval
from app.main.utils import schedule_notification,is_available,get_booked_slots,get_free_time_slots


main = Blueprint('main', __name__)

@bp.route('/create_user',methods=['POST'])
def create_user():
    data = request.json
    user = User(
        name=data['name'],
        email=data['email'],
        preferred_timezone=data['preferred_timezone'],
        dnd_start_time=data['dnd_start_time'],
        dnd_end_time=data['dnd_end_time'],
        meetings=[]
    )
    user.save()
    return jsonify({'message': 'User created successfully!'})

@bp.route('/update_user/<user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.json
    user = User.objects(id=user_id).first()
    if not user:
        return jsonify({'message': 'User not found!'}), 404
    user.update(
        preferred_timezone=data.get('preferred_timezone', user.preferred_timezone),
        dnd_start_time=data.get('dnd_start_time', user.dnd_start_time),
        dnd_end_time=data.get('dnd_end_time', user.dnd_end_time)
    )
    return jsonify({'message': 'User updated successfully!'})

@bp.route('/create_meeting', methods=['POST'])
def create_meeting():
    data = request.json
    creator = User.objects(email=data['creator_email']).first()
    if not creator:
        return {'message': 'Creator not found!'}

    participants = [User.objects(email=email).first() for email in data['participant_emails']]
    participants.append(creator)
    if not all(participants):
        return {'message': 'One or more participants not found!'}

    notification_interval = NotificationInterval(
        interval_type=data['notification_interval']['type'],
        interval_value=data['notification_interval']['value']
    )

    meeting = Meeting(
        title=data['title'],
        meeting_type=data['meeting_type'],
        start_time=datetime.strptime(data['start_time'], '%Y-%m-%d %H:%M:%S'),
        end_time=datetime.strptime(data['end_time'], '%Y-%m-%d %H:%M:%S'),
        timezone=data['timezone'],
        notification_interval=notification_interval,
        creator=creator,
        participants=[]
    )
    if(not is_available(creator,meeting)):
        return {'message': 'You cannot create this meeting because you already have another meeting scheduled at the time'}
    meeting.save()
    unavailable_participants=[]
    for participant in participants:
        if(is_available(participant,meeting)):
            participant_meetings=participant.meetings
            participant_meetings.append(meeting)
            participant.update(meetings=participant_meetings)
            meeting_participants=meeting.participants
            meeting_participants.append(participant)
            meeting.update(participants=meeting_participants)
            schedule_notification(meeting.id, participant, meeting.start_time, meeting.timezone)
        else:
            print(participant.name," is unavailabe")
            unavailable_participants.append(participant.name)

    return {'message': 'Meeting created and notifications scheduled!','unavailable_participants':unavailable_participants}

@bp.route('/get_free_slots', methods=['GET'])
def get_free_slots():
    user_id = request.args.get('user_id')
    start_time = datetime.strptime(request.args.get('start_time'), '%Y-%m-%d %H:%M:%S')
    end_time = datetime.strptime(request.args.get('end_time'), '%Y-%m-%d %H:%M:%S')

    user = User.objects(id=user_id).first()
    if not user:
        return jsonify({'message': 'User not found!'}), 404

    booked_slots=get_booked_slots(user,start_time,end_time)
    free_slots=get_free_time_slots(start_time,end_time,booked_slots)
    return jsonify({'free_slots': free_slots,'booked_meetings':booked_slots})

@bp.route('/meeting/participant/remove',methods=['POST'])
def remove_participant_from_meeting():
    data=request.json
    user=User.objects(id=data["user_id"]).first()
    meeting=Meeting.objects(id=data["meeting_id"]).first()
    

    if not meeting:
        return jsonify({'error': 'Meeting not found'}), 404
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    participant_not_found=True
    for participant in meeting.participants:
        if(participant.id==user.id):
            participant_not_found=False
            break
    if participant_not_found:
        return jsonify({'error':'User is not participant of that meeting'}),404
    
    meeting.participants.remove(user)
    user.meetings.remove(meeting)
    user.save()
    meeting.save()
    return jsonify({'message': 'Participant removed successfully'}), 200

@bp.route('/meeting/participant/add',methods=['POST'])
def add_participant_to_meeting():
    data=request.json
    user=User.objects(id=data["user_id"]).first()
    meeting=Meeting.objects(id=data["meeting_id"]).first()
    participant_found=False
    for participant in meeting.participants:
        if(user.id==participant.id):
            participant_found=True
            break
    if(participant_found):
        return jsonify({'error':'User is already a  participant of that meeting'}),409
    meeting.participants.append(user)
    user.meetings.append(meeting)
    meeting.save()
    user.save()
    return jsonify({'message':'User successfully added to the meeting'}),200



