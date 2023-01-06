from django.db.models.signals import post_save
from django.conf import settings
from django.db import models
from django.db.models import Sum
from django.shortcuts import reverse
from django_countries.fields import CountryField


"""
Declare categories and filters by which the entities can be distinguished.
The main category is coat length, the additional categories are used as filters.
"""
CATEGORY_CHOICES = (
    ('SH', 'Short Hair'),
    ('MH', 'Medium Hair'),
    ('LH', 'Long Hair')
)

ENERGY_CHOICES = (
    ('LE', 'Low Energy'),
    ('ME', 'Medium Energy'),
    ('HE', 'High Energy')
)

SIZE_CHOICES = (
    ('S', 'Small Size'),
    ('M', 'Medium Size'),
    ('L', 'Large Size')
)

GENDER_CHOICES = (
    ('M', 'Boy'),
    ('F', 'Girl')
)

ADDRESS_CHOICES = (
    ('B', 'Billing'),
    ('S', 'Shipping'),
)

# define global constants for min or max durations
MIN_RENTAL_HOURS = 5                # minimum rental duration in hours
MAX_RENTAL_DAYS = 7                 # maximum rental duration in days
MAX_PREORDER_DAYS = 14              # maximum days a cat can be ordered in advance (cat may not be available anymore!)
DEFAULT_RENTAL_DURATION = 1

# date format that is used in front-end
DATE_FORMAT = '%Y-%m-%dT%H:%M'

class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    stripe_customer_id = models.CharField(max_length=50, blank=True, null=True)
    one_click_purchasing = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username


class Item(models.Model):
    title = models.CharField(max_length=100)
    price = models.FloatField(default = 4)
    #price = models.FloatField() TODO: could be used for different hourly rates ?
    #discount_price = models.FloatField(blank=True, null=True)
    available = models.BooleanField(default=True)
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=2)
    label = models.CharField(choices=ENERGY_CHOICES, max_length=2)
    size = models.CharField(choices=SIZE_CHOICES, max_length=1, default='NULL')
    gender = models.CharField(choices=GENDER_CHOICES, max_length=1, default='M')
    slug = models.SlugField()
    description = models.TextField()
    reviews = models.TextField(default="")
    image = models.ImageField()
    image2 = models.ImageField()
    image3 = models.ImageField()
    image4 = models.ImageField()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("core:product", kwargs={
            'slug': self.slug
        })

    def get_add_to_cart_url(self):
        return reverse("core:add-to-cart", kwargs={
            'slug': self.slug
        })

    def get_remove_from_cart_url(self):
        return reverse("core:remove-from-cart", kwargs={
            'slug': self.slug
        })

    def set_unavailable(self):
        self.available = False

    def set_available(self):
        self.available = True

class OrderItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    
    def __str__(self):
        return f"{self.quantity} of {self.item.title}"

    def get_total_item_price(self):
        return self.item.price #self.quantity * self.item.price TODO: Clara - use rental duration and hourly rate?

    def get_duration(self):
        #if(hasattr(self, 'order')):
        if(True):
            return self.order_set.all()[0].get_rental_duration()
        else:
            return 1

    def get_total_discount_item_price(self):
        return 42 #self.quantity * self.item.discount_price

    def get_amount_saved(self):
        return 42 #self.get_total_item_price() - self.get_total_discount_item_price()

    def get_final_price(self):
        """if self.item.discount_price:
            return self.get_total_discount_item_price()
        return self.get_total_item_price()"""
        #return 1
        return self.item.price * self.get_duration()

class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    ref_code = models.CharField(max_length=20, blank=True, null=True)
    items = models.ManyToManyField(OrderItem)
    # start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    #from_date = models.DateTimeField(default=False)
    #to_date = models.DateTimeField(default=False)
    rental_duration = models.IntegerField(default=DEFAULT_RENTAL_DURATION)
    ordered = models.BooleanField(default=False)
    shipping_address = models.ForeignKey(
        'Address', related_name='shipping_address', on_delete=models.SET_NULL, blank=True, null=True)
    billing_address = models.ForeignKey(
        'Address', related_name='billing_address', on_delete=models.SET_NULL, blank=True, null=True)
    payment = models.ForeignKey(
        'Payment', on_delete=models.SET_NULL, blank=True, null=True)
    coupon = models.ForeignKey(
        'Coupon', on_delete=models.SET_NULL, blank=True, null=True)
    being_delivered = models.BooleanField(default=False)
    received = models.BooleanField(default=False)
    refund_requested = models.BooleanField(default=False)
    refund_granted = models.BooleanField(default=False)

    '''
    1. Item added to cart
    2. Adding a billing address
    (Failed checkout)
    3. Payment
    (Preprocessing, processing, packaging etc.)
    4. Being delivered
    5. Received
    6. Refunds
    '''

    def __str__(self):
        return self.user.username

    def get_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_final_price()
        if self.coupon:
            total -= self.coupon.amount
        return total

    def get_rental_duration(self):
        return self.rental_duration


class Address(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    street_address = models.CharField(max_length=100)
    apartment_address = models.CharField(max_length=100)
    country = CountryField(multiple=False)
    zip = models.CharField(max_length=100)
    address_type = models.CharField(max_length=1, choices=ADDRESS_CHOICES)
    default = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name_plural = 'Addresses'


class Payment(models.Model):
    stripe_charge_id = models.CharField(max_length=50)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.SET_NULL, blank=True, null=True)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


class Coupon(models.Model):
    code = models.CharField(max_length=15)
    amount = models.FloatField()

    def __str__(self):
        return self.code


class Refund(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    reason = models.TextField()
    accepted = models.BooleanField(default=False)
    email = models.EmailField()

    def __str__(self):
        return f"{self.pk}"


def userprofile_receiver(sender, instance, created, *args, **kwargs):
    if created:
        userprofile = UserProfile.objects.create(user=instance)


post_save.connect(userprofile_receiver, sender=settings.AUTH_USER_MODEL)
