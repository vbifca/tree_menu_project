from django import template
from django.urls import resolve
from django.utils.safestring import mark_safe
from ..models import Menu, MenuItem

register = template.Library()


class MenuRenderer:
    """Вспомогательный класс для отрисовки меню с правильной логикой разворачивания, используя ровно один запрос к БД."""

    def __init__(self, menu_name, current_url):
        self.menu_name = menu_name
        self.current_url = current_url
        self.menu = None
        self.all_items = []
        self.active_item = None
        self.expanded_items = set()
        self.item_children = {}

    def load_menu_data(self):
        """Загружает данные меню с помощью ровно одного запроса к БД."""
        try:
            # Один запрос для получения всех пунктов меню для этого меню
            self.menu = Menu.objects.get(name=self.menu_name)
            self.all_items = list(MenuItem.objects.filter(menu=self.menu).select_related('parent'))
        except Menu.DoesNotExist:
            return

        # Построение отображения детей
        self._build_children_mapping()

        # Поиск активного элемента и определение развернутых элементов
        self._find_active_item_and_expanded()

    def _build_children_mapping(self):
        """Строит отображение parent_id в список детей."""
        for item in self.all_items:
            parent_id = item.parent_id if item.parent else None
            if parent_id not in self.item_children:
                self.item_children[parent_id] = []
            self.item_children[parent_id].append(item)

        # Сортировка детей по порядку и заголовку
        for parent_id in self.item_children:
            self.item_children[parent_id].sort(key=lambda x: (x.order, x.title))

    def _find_active_item_and_expanded(self):
        """Находит активный пункт меню и определяет, какие элементы должны быть развернуты."""
        # Найти наиболее специфичный активный элемент (самый длинный совпадающий URL)
        active_candidates = []
        for item in self.all_items:
            if item.is_active(self.current_url):
                active_candidates.append(item)

        # Выбрать наиболее специфичный активный элемент (с самым длинным URL)
        if active_candidates:
            self.active_item = max(active_candidates, key=lambda x: len(x.get_url()))
        else:
            self.active_item = None

        if not self.active_item:
            return

        # Развернуть сам активный элемент (чтобы показать его детей)
        self.expanded_items.add(self.active_item.id)

        # Развернуть всех предков активного элемента
        ancestors = self.active_item.get_ancestors(self.all_items)
        for ancestor in ancestors:
            self.expanded_items.add(ancestor.id)

        # Развернуть первый уровень детей под активным элементом
        if self.active_item.id in self.item_children:
            for child in self.item_children[self.active_item.id]:
                self.expanded_items.add(child.id)

    def render_menu_item(self, item, level=0):
        """Отрисовывает отдельный пункт меню рекурсивно."""
        is_active = item == self.active_item
        has_children = item.id in self.item_children
        is_expanded = item.id in self.expanded_items

        # CSS классы
        css_classes = []
        if is_active:
            css_classes.append('active')
        if has_children:
            css_classes.append('has-children')
        if is_expanded:
            css_classes.append('expanded')

        # Отрисовка элемента
        result = f'<li class="{" ".join(css_classes)}">'
        result += f'<a href="{item.get_url()}">{item.title}</a>'

        # Отрисовка детей, если развернуто
        if has_children and is_expanded:
            result += '<ul>'
            for child in self.item_children[item.id]:
                result += self.render_menu_item(child, level + 1)
            result += '</ul>'

        result += '</li>'
        return result

    def render(self):
        """Отрисовывает полное меню."""
        if not self.menu:
            return ''

        # Получить корневые элементы (элементы без родителя)
        root_items = self.item_children.get(None, [])

        result = '<ul class="tree-menu">'
        for item in root_items:
            result += self.render_menu_item(item)
        result += '</ul>'

        return mark_safe(result)


@register.simple_tag(takes_context=True)
def draw_menu(context, menu_name):
    """
    Template tag для отрисовки древовидного меню.
    Использование: {% draw_menu 'main_menu' %}
    """
    request = context.get('request')
    current_url = request.path if request else ''

    renderer = MenuRenderer(menu_name, current_url)
    renderer.load_menu_data()
    return renderer.render()