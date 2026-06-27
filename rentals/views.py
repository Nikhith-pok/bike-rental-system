from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .models import Bike, Customer, Booking, Review
from .forms import UserRegistrationForm, BookingForm, ReviewForm
from django.db.models import Count, Sum, F, ExpressionWrapper, DecimalField
from django.db.models.functions import Coalesce
from django.contrib.admin.views.decorators import staff_member_required

# 1. Home Page / Dashboard
def index(request):
    if request.user.is_authenticated:
        bikes = Bike.objects.all()

        # Search & Filter
        query = request.GET.get('q', '')
        availability = request.GET.get('availability', '')
        min_price = request.GET.get('min_price', '')
        max_price = request.GET.get('max_price', '')

        if query:
            bikes = bikes.filter(make__icontains=query) | bikes.filter(model__icontains=query)
        if availability == 'available':
            bikes = bikes.filter(availability=True)
        elif availability == 'rented':
            bikes = bikes.filter(availability=False)
        if min_price:
            bikes = bikes.filter(daily_rate__gte=min_price)
        if max_price:
            bikes = bikes.filter(daily_rate__lte=max_price)

        return render(request, 'rentals/index.html', {
            'bikes': bikes,
            'query': query,
            'availability': availability,
            'min_price': min_price,
            'max_price': max_price,
        })
    else:
        return render(request, 'rentals/index.html')

# 2. Registration Logic
def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            
            Customer.objects.create(
                user=user,
                phone_number=form.cleaned_data['phone_number']
            )
            
            login(request, user)
            return redirect('index')
    else:
        form = UserRegistrationForm()
    return render(request, 'rentals/register.html', {'form': form})

# 3. New: Bike Details Page (Shows Reviews & Book Button)
@login_required(login_url='/login/')
def bike_details(request, bike_id):
    bike = get_object_or_404(Bike, pk=bike_id)
    reviews = bike.reviews.all().order_by('-created_at')
    
    # Calculate average rating
    avg_rating = 0
    if reviews:
        avg_rating = sum(r.rating for r in reviews) / len(reviews)

    return render(request, 'rentals/bike_details.html', {
        'bike': bike, 
        'reviews': reviews, 
        'avg_rating': round(avg_rating, 1),
    })

# 4. Booking Logic
@login_required(login_url='/login/')
def book_bike(request, bike_id):
    bike = get_object_or_404(Bike, pk=bike_id)
    
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.customer = request.user.customer
            booking.bike = bike
            booking.save()
            return redirect('index')
    else:
        form = BookingForm()
    
    return render(request, 'rentals/book_bike.html', {'form': form, 'bike': bike})

# 5. My Rentals Page
@login_required(login_url='/login/')
def my_rentals(request):
    try:
        bookings = Booking.objects.filter(customer=request.user.customer).select_related('bike')
    except:
        bookings = []
    return render(request, 'rentals/my_rentals.html', {'bookings': bookings})

@login_required(login_url='/login/')
def return_bike(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id, customer=request.user.customer)
    
    # --- NEW: Calculate the Cost ---
    # Calculate the number of days
    delta = booking.end_date - booking.start_date
    days = delta.days
    
    # If returned same day, count as 1 day
    if days == 0:
        days = 1
        
    # Calculate Total
    total_cost = days * booking.bike.daily_rate
    # -------------------------------

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            # Save Review
            review = form.save(commit=False)
            review.bike = booking.bike
            review.user = request.user
            review.save()
            
            # Return Bike
            bike = booking.bike
            bike.availability = True
            bike.save()
            
            # Delete Booking
            booking.delete()
            
            return redirect('my_rentals')
    else:
        form = ReviewForm()
    
    # Pass 'total_cost' and 'days' to the template
    return render(request, 'rentals/return_bike.html', {
        'form': form, 
        'booking': booking,
        'days': days,
        'total_cost': total_cost
    })

@staff_member_required
def dashboard(request):
    total_bikes = Bike.objects.count()
    available_bikes = Bike.objects.filter(availability=True).count()
    total_bookings = Booking.objects.count()
    total_customers = Customer.objects.count()

    # Most booked bikes
    popular_bikes = Bike.objects.annotate(
        booking_count=Count('booking')
    ).order_by('-booking_count')[:5]

    # Total revenue from completed rentals (returned bikes)
    # We calculate per booking: days * daily_rate
    bookings = Booking.objects.select_related('bike').all()
    total_revenue = sum(
        max((b.end_date - b.start_date).days, 1) * float(b.bike.daily_rate)
        for b in bookings
    )

    context = {
        'total_bikes': total_bikes,
        'available_bikes': available_bikes,
        'total_bookings': total_bookings,
        'total_customers': total_customers,
        'popular_bikes': popular_bikes,
        'total_revenue': round(total_revenue, 2),
    }
    return render(request, 'rentals/dashboard.html', context)