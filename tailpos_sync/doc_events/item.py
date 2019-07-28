from tailpos_sync.utils import set_date_updated, set_doc_id


def validate(doc, method):
    set_date_updated(doc)


def before_save(doc, method):
    if doc.in_tailpos:
        set_doc_id(doc)
