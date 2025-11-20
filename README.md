# Django Tree Menu

A Django application for creating and managing hierarchical tree menus with efficient database queries and template tag rendering.

## Features

- **Hierarchical Menu Structure**: Create nested menu items with parent-child relationships
- **Template Tag Rendering**: Use `{% draw_menu 'menu_name' %}` to render menus in templates
- **URL-Based Active Detection**: Automatically highlights active menu items based on current URL
- **Smart Expansion**: Automatically expands parent items above selected item and first-level children
- **Multiple Menus**: Support for multiple named menus on the same page
- **Efficient Queries**: Exactly 1 database query per menu rendering
- **Admin Interface**: Full Django admin integration for menu management
- **Flexible URLs**: Support for both named URLs and explicit URL paths

## Installation

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Add `'menu'` to your `INSTALLED_APPS` in `settings.py`:
   ```python
   INSTALLED_APPS = [
       # ...
       'menu',
   ]
   ```

3. Run migrations:
   ```bash
   python manage.py migrate
   ```

4. Create sample menu data:
   ```bash
   python manage.py populate_menu
   ```

## Usage

### Creating Menus in Admin

1. Go to Django admin (`/admin/`)
2. Add a new Menu with a unique name
3. Add Menu Items with:
   - **Title**: Display text
   - **Parent**: Parent menu item (leave empty for root items)
   - **Named URL**: Django URL pattern name (e.g., `'home'`)
   - **Explicit URL**: Direct URL path (e.g., `'/about/'`)
   - **Order**: Display order within parent

### Template Usage

```django
{% load menu_tags %}

<!-- Render a menu by name -->
{% draw_menu 'main_menu' %}

<!-- Multiple menus on one page -->
{% draw_menu 'main_menu' %}
{% draw_menu 'footer_menu' %}
```

### URL Configuration

Menu items can use either:
- **Named URLs**: Use Django URL pattern names (recommended)
- **Explicit URLs**: Use direct URL paths

Priority: Named URL > Explicit URL

## Menu Expansion Logic

When a menu item is active (based on current URL):
- All parent items above the selected item are expanded
- First level of children under the selected item are expanded

Example:
```
Home
About
Services (expanded)
├── Web Development (active)
│   ├── Frontend Development (expanded)
│   └── Backend Development (expanded)
└── Mobile Apps
Contact
```

## Database Optimization

The menu system uses exactly 1 database query per menu rendering through:
- `prefetch_related` for efficient loading of menu items and their children
- Single query to fetch all menu data at once

## Testing

Run the test suite:
```bash
python manage.py test menu
```

## API Reference

### Models

#### Menu
- `name`: Unique name for the menu
- `description`: Optional description

#### MenuItem
- `menu`: ForeignKey to Menu
- `title`: Display text
- `parent`: Self-referential ForeignKey for hierarchy
- `named_url`: Django URL pattern name
- `explicit_url`: Direct URL path
- `order`: Display order

### Template Tags

#### `draw_menu`
Renders a hierarchical menu by name.

```django
{% draw_menu 'menu_name' %}
```

### Methods

#### `MenuItem.get_url()`
Returns the URL for the menu item (named URL > explicit URL).

#### `MenuItem.is_active(current_url)`
Checks if the menu item is active based on current URL.

#### `MenuItem.get_ancestors()`
Returns all ancestors of the menu item.

#### `MenuItem.get_descendants(include_self=False)`
Returns all descendants of the menu item.