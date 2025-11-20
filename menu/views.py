from django.shortcuts import render


def home(request):
    """Представление главной страницы."""
    return render(request, 'menu/home.html', {'page_title': 'Главная'})


def about(request):
    """Представление страницы "О нас"."""
    return render(request, 'menu/about.html', {'page_title': 'О нас'})


def services(request):
    """Представление страницы услуг."""
    return render(request, 'menu/services.html', {'page_title': 'Наши услуги'})


def web_development(request):
    """Представление страницы веб-разработки."""
    return render(request, 'menu/web_development.html', {'page_title': 'Веб-разработка'})


def mobile_apps(request):
    """Представление страницы мобильных приложений."""
    return render(request, 'menu/mobile_apps.html', {'page_title': 'Мобильные приложения'})


def contact(request):
    """Представление страницы контактов."""
    return render(request, 'menu/contact.html', {'page_title': 'Контакты'})


def frontend_development(request):
    """Представление страницы фронтенд разработки."""
    return render(request, 'menu/frontend_development.html', {'page_title': 'Фронтенд разработка'})


def backend_development(request):
    """Представление страницы бэкенд разработки."""
    return render(request, 'menu/backend_development.html', {'page_title': 'Бэкенд разработка'})


def ios_development(request):
    """Представление страницы iOS разработки."""
    return render(request, 'menu/ios_development.html', {'page_title': 'iOS разработка'})


def android_development(request):
    """Представление страницы Android разработки."""
    return render(request, 'menu/android_development.html', {'page_title': 'Android разработка'})