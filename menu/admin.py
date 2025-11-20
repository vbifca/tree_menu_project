from django.contrib import admin
from django.utils.html import format_html
from .models import Menu, MenuItem


class MenuItemInline(admin.TabularInline):
    """Inline admin для пунктов меню для отображения иерархии."""
    model = MenuItem
    fields = ['title', 'named_url', 'explicit_url', 'order']
    extra = 1
    show_change_link = True


@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    """Admin интерфейс для модели Menu."""
    list_display = ['name', 'description', 'items_count']
    search_fields = ['name', 'description']
    inlines = [MenuItemInline]

    def items_count(self, obj):
        """Отображает количество элементов в этом меню."""
        return obj.items.count()
    items_count.short_description = 'Количество элементов'


class MenuItemAdmin(admin.ModelAdmin):
    """Admin интерфейс для модели MenuItem."""
    list_display = ['title', 'menu', 'parent_display', 'url_display', 'order']
    list_filter = ['menu', 'parent']
    search_fields = ['title', 'named_url', 'explicit_url']
    list_select_related = ['menu', 'parent']
    ordering = ['menu', 'parent', 'order', 'title']

    fieldsets = [
        ('Основная информация', {
            'fields': ['menu', 'title', 'parent', 'order']
        }),
        ('Конфигурация URL', {
            'fields': ['named_url', 'explicit_url'],
            'description': 'Укажите либо именованный URL паттерн, либо явный путь URL.'
        }),
    ]

    def parent_display(self, obj):
        """Отображает родительский пункт меню."""
        return obj.parent.title if obj.parent else "(Корневой)"
    parent_display.short_description = 'Родитель'

    def url_display(self, obj):
        """Отображает URL для этого пункта меню."""
        url = obj.get_url()
        if url and url != '#':
            return format_html('<a href="{}" target="_blank">{}</a>', url, url)
        return "(Нет URL)"
    url_display.short_description = 'URL'

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Ограничивает выбор родителя элементами из того же меню."""
        if db_field.name == "parent":
            # Получить текущий пункт меню, который редактируется
            obj_id = request.resolver_match.kwargs.get('object_id')
            if obj_id:
                try:
                    current_item = MenuItem.objects.get(id=obj_id)
                    # Показывать только элементы из того же меню в качестве возможных родителей
                    kwargs["queryset"] = MenuItem.objects.filter(menu=current_item.menu)
                except MenuItem.DoesNotExist:
                    pass
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


admin.site.register(MenuItem, MenuItemAdmin)