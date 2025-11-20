from django.core.management.base import BaseCommand
from menu.models import Menu, MenuItem


class Command(BaseCommand):
    help = 'Заполняет базу данных примерными данными меню'

    def handle(self, *args, **options):
        # Создать главное меню
        main_menu, created = Menu.objects.get_or_create(
            name='main_menu',
            defaults={'description': 'Главное навигационное меню'}
        )

        if created:
            self.stdout.write(self.style.SUCCESS('Создано main_menu'))

        # Очистить существующие элементы
        MenuItem.objects.filter(menu=main_menu).delete()

        # Создать корневые пункты меню
        home = MenuItem.objects.create(
            menu=main_menu,
            title='Home',
            named_url='home',
            order=0
        )

        about = MenuItem.objects.create(
            menu=main_menu,
            title='About',
            named_url='about',
            order=1
        )

        services = MenuItem.objects.create(
            menu=main_menu,
            title='Services',
            named_url='services',
            order=2
        )

        contact = MenuItem.objects.create(
            menu=main_menu,
            title='Contact',
            named_url='contact',
            order=3
        )

        # Создать подпункты для Services
        web_dev = MenuItem.objects.create(
            menu=main_menu,
            title='Web Development',
            parent=services,
            named_url='web_development',
            order=0
        )

        mobile_apps = MenuItem.objects.create(
            menu=main_menu,
            title='Mobile Apps',
            parent=services,
            named_url='mobile_apps',
            order=1
        )

        # Создать вложенные подпункты
        frontend = MenuItem.objects.create(
            menu=main_menu,
            title='Frontend Development',
            parent=web_dev,
            named_url='frontend_development',
            order=0
        )

        backend = MenuItem.objects.create(
            menu=main_menu,
            title='Backend Development',
            parent=web_dev,
            named_url='backend_development',
            order=1
        )

        ios = MenuItem.objects.create(
            menu=main_menu,
            title='iOS Development',
            parent=mobile_apps,
            named_url='ios_development',
            order=0
        )

        android = MenuItem.objects.create(
            menu=main_menu,
            title='Android Development',
            parent=mobile_apps,
            named_url='android_development',
            order=1
        )

        self.stdout.write(self.style.SUCCESS('Данные меню успешно заполнены'))
        self.stdout.write(f'Создано {MenuItem.objects.count()} пунктов меню')