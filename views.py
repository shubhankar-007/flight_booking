from .serializers import FlightSerializer
from django.db.models import Q
#from rest_framework import generics, permissions, status
# from rest_framework.response import Response
# from rest_framework.authtoken.models import Token
from django.core.mail import send_mail
from .forms import ContactForm
from django.conf import settings
from rest_framework.views import APIView
from django.shortcuts import render, get_object_or_404, redirect
from .models import Flight, Booking, BookingForm
from .forms import FlightForm, ContactForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import CustomUser
from django.db import IntegrityError
from django.http import JsonResponse
from django.contrib.auth.views import LogoutView
from django.contrib.auth.decorators import login_required


def register(request):
    if request.method == "POST":
        username = request.POST['username']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            try:
                CustomUser.objects.create_user(
                    username=username,
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    password=password
                )
                messages.success(request, 'Registration successful. You can now log in.')
                return redirect('login')
            except IntegrityError:
                messages.error(request, 'This email address is already in use. Please choose another.')
        else:
            messages.error(request, 'Passwords do not match.')
    return render(request, 'register.html')


def user_login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Login successful.')
            return redirect('index')
        else:
            messages.error(request, 'Invalid login credentials.')
    return render(request, 'login.html')



def flight_list(request):
    query = request.GET.get('q')  # Get the search query from the request
    flights = Flight.objects.all()

    if query:
        # Filter flights based on the search query (modify the fields as needed)
        flights = flights.filter(
            Q(flight_number__icontains=query) |
            Q(source__icontains=query) |
            Q(destination__icontains=query)
        )

    return render(request, 'flight_list.html', {'flights': flights, 'query': query})

def flight_detail(request, pk):
    flight = get_object_or_404(Flight, pk=pk)
    return render(request, 'flight_detail.html', {'flight': flight})

def create_flight(request):
    if request.method == 'POST':
        form = FlightForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('flights')
    else:
        form = FlightForm()
    return render(request, 'flight_form.html', {'form': form})

def delete_flight(request, pk):
    flight = get_object_or_404(Flight, pk=pk)
    if request.method == 'POST':
        flight.delete()
        return redirect('flights')
    return render(request, 'flight_confirm_delete.html', {'flight': flight})

def update_flight(request, pk):
    flight = get_object_or_404(Flight, pk=pk)
    if request.method == 'POST':
        form = FlightForm(request.POST, instance=flight)
        if form.is_valid():
            form.save()
            return redirect('flights')
    else:
        form = FlightForm(instance=flight)
    return render(request, 'flight_form.html', {'form': form})

@login_required
def book_flight(request, flight_id):
    flight = Flight.objects.get(id=flight_id)
    available_seats = [str(seat_number) for seat_number in range(1, 11)]

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            passenger_name = form.cleaned_data['passenger_name']
            seat_number = form.cleaned_data['seat_number']
            user = request.user

            # Check if the selected seat is available
            if seat_number in available_seats:
                # Check if the seat is already booked
                if not Booking.objects.filter(flight=flight, seat_number=seat_number).exists():
                    booking = Booking(user=user, flight=flight, passenger_name=passenger_name, seat_number=seat_number)
                    booking.save()

                    # Remove the booked seat from the list of available seats
                    available_seats.remove(seat_number)

                    return redirect('my_bookings')  # Redirect to the "My Booking" page

    else:
        form = BookingForm()

    return render(request, 'book_flight.html', {
        'form': form,
        'flight': flight,
        'available_seats': available_seats,
    })

# Add an endpoint to get available seats via AJAX
def get_available_seats(request):
    if request.method == 'GET':
        flight_id = request.GET.get('flight_id')
        booked_seats = Booking.objects.filter(flight_id=flight_id).values_list('seat_number', flat=True)
        available_seats = [str(seat_number) for seat_number in range(1, 11) if str(seat_number) not in booked_seats]
        return JsonResponse({'available_seats': available_seats})
    
@login_required
def my_bookings(request):
    user = request.user
    bookings = Booking.objects.filter(user=user)
    
    booked_seats = [booking.seat_number for booking in bookings]

    context = {
        'bookings': bookings,
        'booked_seats': booked_seats,
    }
    return render(request, 'my_bookings.html', {'bookings': bookings})
    
@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id)
    
    if request.user == booking.user:
        if request.method == 'POST':
            booking.delete()
            return redirect('my_bookings')
        return render(request, 'cancel_booking.html', {'booking': booking})
    else:
        return redirect('my_bookings')
    
from django.shortcuts import render

def index(request):
    return render(request, 'index.html')


def contact_us(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Get cleaned data from the form
            name = form.cleaned_data['name']
            phone = form.cleaned_data['phone']
            email = form.cleaned_data['email']
            message = form.cleaned_data['message']

            # Send an email to the admin
            subject = 'New Contact Form Submission'
            message = f'Name: {name}\nPhone: {phone}\nEmail: {email}\nMessage: {message}'
            from_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = ['shubhankarchaturvedi03@gmail.com']  # Admin's email address
            send_mail(subject, message, from_email, recipient_list, fail_silently=False)

            # Render the same 'contact.html' with a success message
            success_message = 'Thank you for contacting us. We will get back to you as soon as possible.'
            return render(request, 'contact.html', {'form': form, 'success_message': success_message})

    else:
        form = ContactForm()

    return render(request, 'contact.html', {'form': form})


def aboutus(request):
    return render(request, 'about.html')

def privacypolicy(request):
    return render(request, 'privacy-policy.html')

def termsandconditions(request):
    return render(request, 'terms.html')

def custom_logout(request):
    logout(request)
    return redirect('login')