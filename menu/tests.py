from django.test import TestCase, RequestFactory
from django.urls import reverse
from .models import Menu, MenuItem
from .templatetags.menu_tags import MenuRenderer


class MenuModelTests(TestCase):
    def setUp(self):
        self.menu = Menu.objects.create(name='test_menu', description='Test menu')
        self.root_item = MenuItem.objects.create(
            menu=self.menu,
            title='Root Item',
            named_url='home',
            order=0
        )
        self.child_item = MenuItem.objects.create(
            menu=self.menu,
            title='Child Item',
            parent=self.root_item,
            named_url='about',
            order=0
        )

    def test_menu_creation(self):
        """Тестирует создание меню и строковое представление."""
        self.assertEqual(str(self.menu), 'test_menu')

    def test_menu_item_creation(self):
        """Тестирует создание пункта меню и строковое представление."""
        self.assertEqual(str(self.root_item), 'Root Item (test_menu)')

    def test_menu_item_url_resolution(self):
        """Тестирует разрешение URL для пунктов меню."""
        # Тест именованного URL
        self.assertEqual(self.root_item.get_url(), reverse('home'))

        # Тест явного URL
        item_with_explicit_url = MenuItem.objects.create(
            menu=self.menu,
            title='Test',
            explicit_url='/test/'
        )
        self.assertEqual(item_with_explicit_url.get_url(), '/test/')

        # Тест возврата к явному URL, когда именованный URL не существует
        item_with_both = MenuItem.objects.create(
            menu=self.menu,
            title='Test Both',
            named_url='nonexistent',
            explicit_url='/explicit/'
        )
        self.assertEqual(item_with_both.get_url(), '/explicit/')

    def test_menu_item_hierarchy(self):
        """Тестирует методы иерархии пунктов меню."""
        self.assertTrue(self.root_item.is_root)
        self.assertFalse(self.child_item.is_root)

        # Тест предков
        ancestors = self.child_item.get_ancestors()
        self.assertEqual(len(ancestors), 1)
        self.assertEqual(ancestors[0], self.root_item)

    def test_menu_item_active_detection(self):
        """Тестирует определение активного пункта меню."""
        # Тест с совпадающим URL
        current_url = reverse('home')
        self.assertTrue(self.root_item.is_active(current_url))

        # Тест с несовпадающим URL
        self.assertFalse(self.root_item.is_active('/completely-different-url/'))

        # Тест с элементом без URL
        item_no_url = MenuItem.objects.create(
            menu=self.menu,
            title='No URL'
        )
        self.assertFalse(item_no_url.is_active('/any/'))


class MenuRendererTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.menu = Menu.objects.create(name='test_menu', description='Test menu')

        # Create a simple hierarchy
        self.root1 = MenuItem.objects.create(
            menu=self.menu,
            title='Root 1',
            named_url='home',
            order=0
        )
        self.root2 = MenuItem.objects.create(
            menu=self.menu,
            title='Root 2',
            named_url='about',
            order=1
        )
        self.child1 = MenuItem.objects.create(
            menu=self.menu,
            title='Child 1',
            parent=self.root1,
            named_url='services',
            order=0
        )

    def test_menu_renderer_initialization(self):
        """Test menu renderer initialization."""
        renderer = MenuRenderer('test_menu', '/home/')
        renderer.load_menu_data()
        self.assertEqual(renderer.menu, self.menu)

    def test_menu_renderer_with_nonexistent_menu(self):
        """Test menu renderer with non-existent menu."""
        renderer = MenuRenderer('nonexistent', '/home/')
        renderer.load_menu_data()
        self.assertIsNone(renderer.menu)

    def test_active_item_detection(self):
        """Test active item detection in menu renderer."""
        renderer = MenuRenderer('test_menu', reverse('services'))
        renderer.load_menu_data()
        self.assertEqual(renderer.active_item, self.child1)

    def test_expansion_logic(self):
        """Test menu expansion logic."""
        renderer = MenuRenderer('test_menu', reverse('services'))
        renderer.load_menu_data()

        # Should expand parent of active item
        self.assertIn(self.root1.id, renderer.expanded_items)

        # Should expand first-level children of active item
        # (in this case, active item has no children, so no additional expansions)

    def test_menu_rendering(self):
        """Test menu rendering output."""
        renderer = MenuRenderer('test_menu', reverse('home'))
        renderer.load_menu_data()
        output = renderer.render()

        # Should contain menu structure
        self.assertIn('tree-menu', output)
        self.assertIn('Root 1', output)
        self.assertIn('Root 2', output)


class TemplateTagTests(TestCase):
    def test_draw_menu_tag(self):
        """Test the draw_menu template tag."""
        from django.template import Context, Template

        # Create a simple menu
        menu = Menu.objects.create(name='test_tag_menu')
        MenuItem.objects.create(menu=menu, title='Test Item', named_url='home')

        template = Template(
            '{% load menu_tags %}' +
            '{% draw_menu "test_tag_menu" %}'
        )

        # Create a mock request context
        request = RequestFactory().get('/')
        context = Context({'request': request})

        result = template.render(context)
        self.assertIn('tree-menu', result)
        self.assertIn('Test Item', result)