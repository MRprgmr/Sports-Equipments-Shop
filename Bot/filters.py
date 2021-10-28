from django.contrib.admin import SimpleListFilter

from Bot.models import Category


class CategoryFilter(SimpleListFilter):
    """Filter which extracts products in specific category"""

    title = "Kategoriyalar"

    parameter_name = 'products_in_category'

    def lookups(self, request, model_admin):
        categories = Category.objects.all()

        return ((category.id, category.title) for category in categories)

    def queryset(self, request, queryset):
        if self.value() is not None:
            category = Category.objects.get(id=self.value())
            custom_list = [product.id for product in category.products.all()]
            return queryset.filter(id__in=custom_list)
