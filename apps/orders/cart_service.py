from decimal import Decimal
from apps.cart.cart import Cart
from apps.orders.models import Order, OrderItem

def process_cart_for_order(request):
    """
    Process the cart for creating an order.
    Validates stock and ensures the cart is not empty.
    """
    cart = Cart(request)

    # Ensure the cart is not empty
    if not cart.cart or not any(
        cart.cart.values()
    ):  #  falsy evaluates to true if cart is empty
        raise ValueError("The cart is empty.")

    # Check stock availability for each item in the cart
    for item in cart:
        product = item["product"]
        quantity = item["quantity"]

        # Check if enough stock available
        if product.in_stock < quantity:
            raise ValueError(
                f"Not enough stock for {product.name}. Available: {product.in_stock}"
            )

    return cart

def create_order_from_cart(cart, shipping_address, user_profile):
    """
    Create an order from the cart and reduce stock for purchased items.
    """
    # Create the order
    # Save the state and shipping fee in case the address is deleted or updated
    order = Order.objects.create(
        customer=user_profile,
        state=shipping_address.state,
        city=shipping_address.city,
        street_address=shipping_address.street_address,
        shipping_fee=shipping_address.shipping_fee,
        phone_number=shipping_address.phone_number,
        postal_code=shipping_address.postal_code,
    )

    # Add items from the cart to the order
    for item in cart:
        product = item["product"]
        quantity = item["quantity"]
        price = Decimal(item["price"])

        # Create order item and reduce stock
        OrderItem.objects.create(
            order=order, product=product, quantity=quantity, price=price
        )
        product.in_stock -= quantity
        product.save()

    # Clear the cart after creating the order
    cart.clear()
    
    return order