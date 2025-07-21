from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return self.name


class Order(models.Model):
    # Required fields
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()
    postal_code = models.CharField(max_length=20)

    # Optional fields
    billing_address = models.TextField(blank=True, null=True)
    delivery_instructions = models.TextField(blank=True, null=True)
    order_notes = models.TextField(blank=True, null=True)
    delivery_time = models.CharField(max_length=100, blank=True, null=True)

    # System fields
    total = models.DecimalField(max_digits=10, decimal_places=2)
    payment_intent_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} by {self.name}"

# class ContactMessage(models.Model):
#     name = models.CharField(max_length=100)
#     email = models.EmailField()
#     message = models.TextField()
#     created_at = models.DateTimeField(auto_now_add=True)
class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.name}"
