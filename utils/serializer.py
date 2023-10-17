from datetime import datetime

def serializer(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    return obj.__dict__