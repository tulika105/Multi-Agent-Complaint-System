import uuid


def generate_complaint_id():
    unique_id = str(uuid.uuid4())[:6].upper()
    return f"CMP-{unique_id}"