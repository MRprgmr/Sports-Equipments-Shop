from django.conf import settings
from django.contrib import admin
from django.contrib.auth.models import Group

from Bot.models import Order, User, Category, Product
from .filters import CategoryFilter

admin.site.unregister(Group)
admin.site.site_header = settings.PROJECT_NAME
admin.site.site_title = settings.PROJECT_NAME
admin.site.index_title = "Xush Kelibsiz"


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Bot User"""

    list_display = ['first_name', 'username', 'contact', 'lang', 'user_id']
    exclude = ['product_cart']
    search_fields = ['user_id', 'username', 'fullname', 'contact', 'lang']
    list_filter = ['lang']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Product Category"""

    def status_list(self, obj):
        d_status = {0: "✖️", 1: "✅"}
        return d_status[obj.status]

    status_list.short_description = "Status"

    list_display = ['title', 'status_list']
    search_fields = ['title']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Product"""

    def price_(self, obj):
        return f"{obj.price} {obj.currency}"

    price_.short_description = 'Narxi'

    list_display = ['title', 'price_']
    search_fields = ['title', 'description', 'price', 'category__title']
    list_filter = [CategoryFilter]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Order"""

    def custom_price(self, obj):
        return f"{obj.total_cost} so'm"

    custom_price.short_description = "To'langan summa"

    list_display = ('id', 'user', 'custom_price', 'creation_date')
    exclude = ('ordered_products', 'total_cost',)
    readonly_fields = ('id', 'user', 'custom_price', 'creation_date', 'address_location', 'products_list')
