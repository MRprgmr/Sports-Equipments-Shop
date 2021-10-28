from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

class Category(models.Model):
    """Category of product"""

    title = models.CharField(
        max_length=100, verbose_name="Kategoriya", unique=True)
    status = models.BooleanField(verbose_name="Status", choices=(
        (False, "✖️ O'chirilgan"), (True, "✅ Faol")), default=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Kategoriya"
        verbose_name_plural = "Kategoriyalar"


class Product(models.Model):
    """Model of products"""

    category = models.ForeignKey(
        Category, related_name='products', on_delete=models.CASCADE)
    title = models.CharField(max_length=100, verbose_name='Nomi', unique=True)
    description = models.TextField(max_length=1000, verbose_name='Tavsifi')
    link = models.CharField(verbose_name='Telegra.ph havola',
                            max_length=255, null=True, blank=True)
    price = models.IntegerField(verbose_name='Narxi', validators=[
                                MinValueValidator(1), MaxValueValidator(100000000)])
    currency = models.CharField(verbose_name='Valyuta', max_length=5, choices=(
        ("so'm", "So'm"), ('$', "Dollar")), default="so'm")
    image = models.ImageField(
        verbose_name="Maxsulot rasmi", upload_to='images')

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['id']
        verbose_name = "Maxsulot"
        verbose_name_plural = "Maxsulotlar"


class User(models.Model):
    """Model User"""

    user_id = models.IntegerField(verbose_name='ID User', primary_key=True)
    username = models.CharField(
        max_length=100, verbose_name='@username', null=True, blank=True)
    first_name = models.CharField(
        max_length=100, verbose_name='Name in Telegram')
    contact = models.CharField(
        max_length=100, verbose_name='Contact', null=True, blank=True)
    full_name = models.CharField(
        max_length=255, verbose_name='Full Name', null=True, blank=True)
    is_registered = models.BooleanField(
        verbose_name="Is Registered", default=False)
    lang = models.CharField(max_length=100, verbose_name='Language', choices=(('ru', 'Русский'), ('uz', "O'zbekcha")),
                            null=True)
    product_cart = models.ManyToManyField(Product)

    def __str__(self) -> str:
        """Describe the user in the best way possible given the available data."""
        return self.full_name if self.full_name else self.first_name

    def mention_link(self) -> str:
        """Mention the user in the best way possible given the available data."""
        return f"tg://user?id={self.user_id}"

    class Meta:
        verbose_name = "Foydalanuvchi"
        verbose_name_plural = "Foydalanuvchilar"


class Order(models.Model):
    "Models order"

    id=models.BigAutoField(primary_key=True, verbose_name='Buyurtma raqami')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Foydalanuvchi", related_name='orders')
    total_cost = models.IntegerField(verbose_name='Narxi')
    creation_date = models.DateTimeField(verbose_name='Sanasi', auto_now_add=True)
    address_location = models.TextField(verbose_name="Manzili", max_length=10000) 
    ordered_products = models.ManyToManyField(Product)

    def __str__(self):
        return f"{self.user}  #{self.id}"

    @property
    def products_list(self):
        return "\n".join([f"    {str(i+1)}. {str(item)}" for i, item in enumerate(self.ordered_products.all())])
    products_list.fget.short_description = "Olingan maxsulotlar"

    class Meta:
        verbose_name = "Buyurtma"
        verbose_name_plural = "Buyurtmalar"