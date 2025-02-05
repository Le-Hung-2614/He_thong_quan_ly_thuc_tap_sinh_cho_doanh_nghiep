# home/utils.py
from django.contrib.auth.models import Group

def get_user_groups_context(user):
    """
    Trả về một dictionary chứa thông tin về các nhóm người dùng.
    """
    return {
        'is_admin': user.is_superuser,
        'is_hr_manager': user.groups.filter(name='HR Managers').exists(),
        'is_intern': user.groups.filter(name='Interns').exists(),
        'is_internship_coordinator': user.groups.filter(name='Internship Coordinators').exists(),
        'is_mentor': user.groups.filter(name='Mentors').exists(),
    }