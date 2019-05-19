import uuid


def validate(doc, method):
    if doc.date_updated is None:
        doc.date_updated = doc.modified


def before_save(doc, method):
    if doc.in_tailpos and not doc.id:
        doc.id = str(uuid.uuid4())
