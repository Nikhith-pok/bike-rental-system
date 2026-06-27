from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='rentals/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='index'), name='logout'),
    
    path('book/<int:bike_id>/', views.book_bike, name='book_bike'),
    path('my-rentals/', views.my_rentals, name='my_rentals'),

    # CHANGED: Return logic now points to a view that handles the review first
    path('return/<int:booking_id>/', views.return_bike, name='return_bike'),

    # NEW: Bike Details Page
    path('bike/<int:bike_id>/', views.bike_details, name='bike_details'),

    path('dashboard/', views.dashboard, name='dashboard'),
]