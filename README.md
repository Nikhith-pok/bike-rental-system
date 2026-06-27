# Bike Rental System

A full-stack bike rental platform built with Django where users can browse bikes, make bookings, and leave reviews after returning them. Admins get a separate dashboard to monitor revenue, bookings, and fleet usage.

I built this to get hands-on with Django's ORM, user authentication, and session management — basically to understand how a real web app fits together end to end.

---

## Features

**For users:**
- Register and log in to access the platform
- Browse all bikes with availability badges and daily pricing
- Search bikes by make or model name, and filter by min/max price per day
- Select rental dates on the booking page — a live cost calculator shows the total cost before confirming (no page reload)
- View all your active bookings in a dedicated "My Rentals" page
- Return a bike and leave a star rating (1–5) + written review which shows up on the bike's detail page

**For admins:**
- Staff-only dashboard at `/dashboard/` showing total bikes, active bookings, and registered customers
- Revenue tracker that calculates total earnings from all bookings based on duration × daily rate
- Ranked table of top 5 most booked bikes using Django ORM annotations

---

## Tech Stack

- **Backend:** Python, Django 5.2
- **Database:** SQLite via Django ORM
- **Frontend:** HTML, CSS, JavaScript (vanilla — no React or jQuery)
- **UI:** Bootstrap 5.3, Font Awesome 6

---

## How to run locally

```bash
git clone https://github.com/Nikhith-pok/bike-rental-system.git
cd bike-rental-system

pip install django

python manage.py migrate

# Create an admin account to access /dashboard/
python manage.py createsuperuser

python manage.py runserver
```

Visit http://127.0.0.1:8000/ and register a new account to start browsing bikes.
To access the admin dashboard, log in with your superuser credentials — the Dashboard link appears in the navbar.

---

## Database Models

- **Customer** — extends Django's built-in User model with a phone number field via OneToOneField
- **Bike** — stores make, model, year, daily rate, availability status, and an optional image URL
- **Booking** — links a customer to a bike with start and end dates; the `save()` method automatically flips the bike's availability to False when a booking is created
- **Review** — stores a star rating (1–5) and a comment per bike per user, with a timestamp; the bike detail page shows all reviews along with the calculated average rating

---

## Things worth noting

- The booking form uses vanilla JavaScript to calculate rental cost in real time as the user picks dates — `(end - start) in days × daily rate` — updates instantly without any backend call
- Search and filtering on the home page is done through Django ORM query chaining (`filter`, `icontains`, `gte`, `lte`) rather than raw SQL
- The admin dashboard uses `annotate(Count('booking'))` to rank bikes by number of bookings, and calculates revenue by iterating over bookings and summing `days × daily_rate`
- Used `select_related('bike')` in the My Rentals view to avoid N+1 queries when loading bookings with their associated bike data

---

## What I'd improve with more time

- Add pagination to the bike listing page
- Send email confirmations when a booking is made
- Deploy it properly on Railway or Render with a PostgreSQL database instead of SQLite

---

Made by Nikhith Reddy — [GitHub](https://github.com/Nikhith-pok) | nikhith.naru@gmail.com
