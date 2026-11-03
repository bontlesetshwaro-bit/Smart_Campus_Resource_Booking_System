"""
user_models.py - The user classes (classes, inheritance and encapsulation).
"""


class User:
    """Parent class. The id and username are private (encapsulation)."""

    def __init__(self, user_id, username, role, campus_id):
        self.__user_id = user_id
        self.__username = username
        self.role = role
        self.campus_id = campus_id

    def get_id(self):
        return self.__user_id

    def get_username(self):
        return self.__username

    # What each role may do. The child classes change these answers.
    def can_book(self):
        return False

    def can_manage_resources(self):
        return False

    def can_view_all_campuses(self):
        return False


class Lecturer(User):
    def can_book(self):
        return True


class CampusAdmin(User):
    def can_manage_resources(self):
        return True


class SystemOperator(User):
    def can_view_all_campuses(self):
        return True


def make_user(row):
    """Turn a database row (id, username, role, campus_id) into a user object."""
    user_id, username, role, campus_id = row
    if role == "Lecturer":
        return Lecturer(user_id, username, role, campus_id)
    if role == "Campus Admin":
        return CampusAdmin(user_id, username, role, campus_id)
    return SystemOperator(user_id, username, role, campus_id)
