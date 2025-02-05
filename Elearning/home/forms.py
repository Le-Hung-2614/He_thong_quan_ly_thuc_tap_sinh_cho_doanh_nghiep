from django import forms
from .models import Recruitment

class RecruitmentForm(forms.ModelForm):
    class Meta:
        model = Recruitment
        fields = ['position', 'description', 'requirements', 'location', 'salary_range', 'deadline', 'is_active']
