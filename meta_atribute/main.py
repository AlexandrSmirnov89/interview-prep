from datetime import datetime


class TimestampMeta(type):
    def __new__(cls, name, bases, attrs):
        attrs['created_at'] = datetime.now()
        return super().__new__(cls, name, bases, attrs)

