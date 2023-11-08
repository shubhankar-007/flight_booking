from rest_framework import serializers
from django import forms
from .models import CustomUser, Flight, Booking, ContactSubmission

class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = '__all__'
        

class FlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flight
        fields = '__all__'


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = '__all__'



class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactSubmission
        fields = ('name', 'phone_number', 'email', 'message')
