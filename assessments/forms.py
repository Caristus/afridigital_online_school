from django import forms
from .models import Submission

class SubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ['text_answer', 'file_upload']
        widgets = {
            'text_answer': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 10,
                'placeholder': 'Type your answer here...'
            }),
            'file_upload': forms.FileInput(attrs={
                'class': 'form-control'
            })
        }
