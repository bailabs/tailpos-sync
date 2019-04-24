def add_role(doc, method):
    """
    Used in hooks for User
    """
    doc.add_roles('Subscriber')
    doc.save()
