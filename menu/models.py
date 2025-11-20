from django.db import models
from django.urls import reverse, NoReverseMatch
from django.utils.text import slugify


class Menu(models.Model):
    """Представляет именованное меню, которое может содержать несколько пунктов меню."""
    name = models.CharField(max_length=100, unique=True, help_text="Уникальное имя для этого меню")
    description = models.TextField(blank=True, help_text="Опциональное описание этого меню")

    class Meta:
        verbose_name = "Меню"
        verbose_name_plural = "Меню"

    def __str__(self):
        return self.name


class MenuItem(models.Model):
    """Представляет отдельный пункт в иерархической структуре меню."""
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE, related_name='items')
    title = models.CharField(max_length=100, help_text="Текст для отображения пункта меню")
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        help_text="Родительский пункт меню (оставьте пустым для корневых элементов)"
    )

    # Конфигурация URL
    named_url = models.CharField(
        max_length=100,
        blank=True,
        help_text="Именованный URL паттерн Django (например, 'home')"
    )
    explicit_url = models.CharField(
        max_length=200,
        blank=True,
        help_text="Явный путь URL (например, '/about/')"
    )

    # Сортировка
    order = models.PositiveIntegerField(default=0, help_text="Порядок внутри родительского меню")

    class Meta:
        verbose_name = "Пункт меню"
        verbose_name_plural = "Пункты меню"
        ordering = ['order', 'title']

    def __str__(self):
        return f"{self.title} ({self.menu.name})"

    def get_url(self):
        """
        Возвращает URL для этого пункта меню.
        Приоритет: named_url > explicit_url
        """
        if self.named_url:
            try:
                return reverse(self.named_url)
            except NoReverseMatch:
                # Возврат к явному URL, если именованный URL не существует
                pass

        if self.explicit_url:
            return self.explicit_url

        return '#'

    def is_active(self, current_url):
        """
        Проверяет, является ли этот пункт меню активным на основе текущего URL.
        """
        if not current_url:
            return False

        item_url = self.get_url()
        if not item_url or item_url == '#':
            return False

        # Нормализация URL для сравнения - убедиться, что они имеют ведущие слеши
        current_url = current_url.rstrip('/')
        item_url = item_url.rstrip('/')

        # Обработка корневого URL
        if item_url == '':
            item_url = '/'
        if current_url == '':
            current_url = '/'

        # Точное совпадение
        if current_url == item_url:
            return True

        # Обработка случаев, когда текущий URL начинается с URL элемента (для вложенных страниц)
        # Считаем активным только если:
        # 1. URL элемента не просто '/'
        # 2. Текущий URL начинается с item_url + '/' (а не просто тот же префикс)
        if item_url != '/' and current_url.startswith(item_url + '/'):
            return True

        return False

    @property
    def is_root(self):
        """Проверяет, является ли этот пункт меню корневым."""
        return self.parent is None

    def get_ancestors(self, all_items=None):
        """Получает всех предков этого пункта меню."""
        ancestors = []
        current = self.parent
        while current:
            ancestors.append(current)
            # Если у нас есть all_items, используем его, чтобы избежать запросов к БД
            if all_items:
                current = next((item for item in all_items if item.id == current.parent_id), None) if current.parent_id else None
            else:
                current = current.parent
        return ancestors[::-1]  # Возвращаем от корня к родителю