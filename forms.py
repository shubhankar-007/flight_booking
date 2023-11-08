from django import forms
from .models import Flight

class FlightForm(forms.ModelForm):
    class Meta:
        model = Flight
        fields = '__all__'
        
class ContactForm(forms.Form):
    name = forms.CharField(label='Your Name', max_length=100)
    phone = forms.CharField(label='Phone', max_length=15)
    email = forms.EmailField(label='Email')
    message = forms.CharField(label='Message', widget=forms.Textarea)       