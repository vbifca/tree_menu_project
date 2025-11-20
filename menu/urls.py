from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('services/', views.services, name='services'),
    path('services/web-development/', views.web_development, name='web_development'),
    path('services/web-development/frontend/', views.frontend_development, name='frontend_development'),
    path('services/web-development/backend/', views.backend_development, name='backend_development'),
    path('services/mobile-apps/', views.mobile_apps, name='mobile_apps'),
    path('services/mobile-apps/ios/', views.ios_development, name='ios_development'),
    path('services/mobile-apps/android/', views.android_development, name='android_development'),
    path('contact/', views.contact, name='contact'),
]