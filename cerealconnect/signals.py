from django.db.models.signals import post_migrate
from django.dispatch import receiver
from cerealconnect.models import Category


@receiver(post_migrate)
def create_default_categories(sender, **kwargs):
    categories_list = [
        'Maize', 'Beans', 'Millet', 'Sorghum', 'Barley',
        'Oats', 'Wheat', 'Rice', 'Quinoa', 'Amaranth',
        'Buckwheat', 'Spelt', 'Teff', 'Chia Seeds', 'Flax Seeds'
    ]

    for category_name in categories_list:
        Category.objects.get_or_create(name=category_name)
