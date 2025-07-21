from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Order
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY

from django.contrib import messages  # import this
from .forms import ContactMessageForm
from django.core.mail import send_mail

def home(request):
    products = Product.objects.all()
    form = ContactMessageForm()

    if request.method == 'POST' and 'contact_submit' in request.POST:
        form = ContactMessageForm(request.POST)
        if form.is_valid():
            message = form.save()
            # send email, add messages, redirect

            # Optional email sending
            send_mail(
                subject=f"New Contact Message from {message.name}",
                message=f"From: {message.name} <{message.email}>\n\nMessage:\n{message.message}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.CONTACT_RECEIVER_EMAIL],
                fail_silently=False,
            )

            messages.success(request, "Thanks! Your message has been sent successfully.")
            return redirect('home')  # Redirect to home so form isn't re-posted

    return render(request, "store/home.html", {
        "products": products,
        "form": form,
    })

def cart(request):
    cart = request.session.get("cart", {})
    cart_items = []
    total = 0

    for product_id, item in cart.items():
        try:
            product = Product.objects.get(id=product_id)
            quantity = int(item['quantity'])
            subtotal = product.price * quantity
            cart_items.append({
                "product": product,
                "quantity": quantity,
                "subtotal": subtotal
            })
            total += subtotal
        except Product.DoesNotExist:
            continue

    # ✅ Handle Checkout Form Submission
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        address = request.POST.get("shipping_address")
        postal_code = request.POST.get("postal_code")
        billing_address = request.POST.get("billing_address")
        delivery_instructions = request.POST.get("delivery_instructions")
        order_notes = request.POST.get("order_notes")
        delivery_time = request.POST.get("preferred_time")
        payment_method_id = request.POST.get("payment_method_id")

        try:
            intent = stripe.PaymentIntent.create(
            amount=int(total * 100),
            currency='usd',
            payment_method=payment_method_id,
            confirmation_method='manual',
            confirm=True,
            payment_method_types=['card'],  # ✅ Use this instead of automatic_payment_methods
        )
            if intent.status != 'succeeded':
                return render(request, "store/error.html", {
                    "message": f"Payment failed or requires additional action. Status: {intent.status}"
                })

            order = Order.objects.create(
                name=name,
                email=email,
                phone=phone,
                address=address,
                postal_code=postal_code,
                billing_address=billing_address,
                delivery_instructions=delivery_instructions,
                order_notes=order_notes,
                delivery_time=delivery_time,
                payment_intent_id=intent.id,
                total=total
            )

            request.session['cart'] = {}
            return redirect('payment_success', order_id=order.id)

        except stripe.error.CardError as e:
            return render(request, "store/error.html", {"message": e.user_message})
        except Exception as e:
            return render(request, "store/error.html", {"message": str(e)})
# GET request
    context = {
        "cart_items": cart_items,
        "cart_total": total,
        "stripe_pub_key": settings.STRIPE_PUBLISHABLE_KEY,
        "required_fields": ['name', 'email', 'phone', 'shipping_address', 'postal_code'],
        "optional_fields": ['billing_address', 'delivery_instructions', 'order_notes', 'preferred_time'],
    }

    return render(request, "store/cart.html", context)

def payment_success(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'store/success.html', {'order': order})

def add_to_cart(request, product_id):
    if request.method == 'POST':
        price = request.POST.get('price')
        try:
            quantity = int(request.POST.get('quantity', 1))
        except (ValueError, TypeError):
            quantity = 1  # fallback in case of bad input

        cart = request.session.get('cart', {})

        # Replace existing quantity instead of adding
        cart[str(product_id)] = {
            'price': price,
            'quantity': quantity
        }

        request.session['cart'] = cart
        request.session.modified = True

    return redirect('cart')

def update_cart(request, product_id):
    if request.method == "POST":
        qty = int(request.POST.get("quantity"))
        cart = request.session.get("cart", {})
        if qty > 0:
            if str(product_id) in cart:
                cart[str(product_id)]['quantity'] = qty
        else:
            cart.pop(str(product_id), None)
        request.session["cart"] = cart
    return redirect("cart")

def remove_from_cart(request, product_id):
    cart = request.session.get("cart", {})
    cart.pop(str(product_id), None)
    request.session["cart"] = cart
    return redirect("cart")
