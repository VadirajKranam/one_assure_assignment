from mongoengine import Document, StringField, DateTimeField, ListField, ReferenceField, EmbeddedDocument, EmbeddedDocumentField, EmbeddedDocumentListField
from datetime import datetime

class NotificationInterval(EmbeddedDocument):
    interval_type = StringField(required=True, choices=('crontab', 'custom'))
    interval_value = StringField(required=True)

class User(Document):
    name = StringField(required=True)
    email = StringField(required=True, unique=True)
    preferred_timezone = StringField(required=True)
    dnd_start_time = StringField(required=True)
    dnd_end_time = StringField(required=True)
    meetings = ListField(ReferenceField('Meeting'))


class Meeting(Document):
    title = StringField(required=True)
    meeting_type = StringField(required=True, choices=('online', 'offline'))
    start_time = DateTimeField(required=True)
    end_time = DateTimeField(required=True)
    timezone = StringField(required=True)
    notification_interval = EmbeddedDocumentField(NotificationInterval)
    creator = ReferenceField(User, required=True)
    participants = ListField(ReferenceField(User))
