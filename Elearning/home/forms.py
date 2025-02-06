from django import forms
from .models import Recruitment
from django.utils import timezone

class RecruitmentForm(forms.ModelForm):
    class Meta:
        model = Recruitment
        fields = ['position', 'description', 'requirements', 'location', 'salary_range', 'deadline']
        
    def clean_deadline(self):
        deadline = self.cleaned_data.get('deadline')
        if deadline < timezone.now().date():
            raise forms.ValidationError("Hạn nộp không được ở trong quá khứ.")
        return deadline