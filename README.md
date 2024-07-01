API Endpoints

Create User

Description: Create a user with unique email id, specify when he/she does not want to be disturbed.

Endpoint: /api/create_user

request.body:
email: User’s E-mail address (unique)
name:username
timezone:user's preferred timezone
dnd_start_time: The Do Not Disturb start time in hour format.
dnd_end_time: The Do Not Disturb end time in hour format.

Create Meeting

Description: Create a meetng for certain time range. It throws error if the meeting creator has already planned another meeting at the same term if any of the participant is unavailable meeting will still be created but the api will respond with array of unavailable participants
Endpoint: /api/create_meeting

request.body:

creator_id: ID of the creator.

start_time: Start time of the meeting .

end_time: End time of the meeting .
time_zone:time zone
participants: An array of email ids of participants.
notification_interval:which has type of notification couldn't complete this part where i had to send the notification in the given interval
Scheduler

Description: This schedules reminders one hour before meetings start, obeying users’ DND times.

Get Free Slots

Description: Retrieve booked meetings and free slots within given interval for a user.

Endpoint: /api/get_free_slots

request.body:

`user_id’: ID of a user.

‘start_time’: Start time from which to check free slots (ISO format).

‘end_time‘: End-time against which to check free slots (ISO format).

Add User to Meeting

Description:  Add an existing user to a meeting. Throws an error if the user is already a participant or user is not in the system.
Endpoint: /api/meeting/participant/add

request.body:

'user_id': ID of the user to be added.

'meeting_id’: ID for the meeting where the user will be included.

Remove User from Meeting

Description: Removing a participant from a meeting. If the given user is not found in the system or not a participant of the given meeting, an error is thrown.

Endpoint: /api/meeting/participant/remove
request.body:

'user_id': ID of the user to be added.

'meeting_id’: ID for the meeting where the user will be included.

Lessons Learned
MongoDB with MongoEngine ORM
I have used MongoDB with MongoEngine ORM so that creation, update and delete operations can be carried out on database collections without any interruptions which is a new thing for me as i have never used mongo with flask.
Task Scheduling with APScheduler
Integrated Flask’s APScheduler which entails notifications before scheduled events take place automatically thereby keeping them up to date at all times. Note that scheduler instances are tied to the Flask app's runtime and require persistence to survive app restarts.
Challenges Faced
There were intricacies in dealing with different time zones of users’ and meetings, which called for accurate conversion to produce correct endpoint responses.
