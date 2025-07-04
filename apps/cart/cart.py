import json
from decimal import Decimal

import redis
from django.conf import settings

from apps.shop.models import Product


class Cart:

    def __init__(self, request):
        """
        Initialize the cart.
        """

        # Connect to Redis
        self.redis_client = redis.StrictRedis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            decode_responses=True,  # Ensures data is stored as strings
        )

        # Create a unique key for the cart
        # self.cart_key = (
        #     f"cart_{request.user.id}" if request.user.is_authenticated else None
        # )
        self.cart_key = (
            f"cart_{request.user.id}"
            if request.user.is_authenticated
            else f"cart_guest_{request.session.session_key}"
        )

        # Try to get the cart from Redis
        cart = self.redis_client.get(self.cart_key)
        # print(cart)

        if cart:
            # Load the cart from Redis if it exists
            self.cart = json.loads(cart)
        else:
            # Create an empty cart if not found
            self.cart = {}
            self.redis_client.set(
                self.cart_key, json.dumps(self.cart)
            )  # Save the empty cart in Redis

    def add(self, product, quantity=1, override_quantity=False):
        """
        Add a product to the cart or update its quantity.
        """
        # Convert product ID to string (Redis requires string keys)
        # By default we have to store in string to redis
        product_id = str(product.id)

        if product_id not in self.cart:
            self.cart[product_id] = {
                "quantity": 0,
                "price": str(product.price),
                "discounted_price": (
                    str(product.discounted_price)
                    if (product.discounted_price != None)
                    else str(0)
                ),
            }

        if override_quantity:  # updating items directly from cart page
            self.cart[product_id]["quantity"] = quantity
        else:  # adding more items to cart
            self.cart[product_id]["quantity"] += quantity

        self.save()

    def save(self):
        """
        Save the cart to Redis.
        """
        self.redis_client.set(self.cart_key, json.dumps(self.cart))

    def remove(self, product):
        """
        Remove a product from the cart.
        Returns True if product was removed, False if product wasn't in cart.
        """
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()
            return True
        return False

    def __iter__(self):
        """
        Iterate over the items in the cart and get the products
        from the database.
        """
        # convert the items in the cart from str to decimal
        product_ids = self.cart.keys()
        # get the product objects and add them to the cart
        products = Product.objects.filter(id__in=product_ids).select_related('category')
        cart = self.cart.copy()

        # First update prices in self.cart (without product objects)
        for product in products:
            product_id = str(product.id)
            # Update the stored price with the current price from the database
            cart[product_id]["price"] = str(product.price)
            cart[product_id]["discounted_price"] = (
                str(product.discounted_price) if product.discounted_price else str(0)
            )

        # Save the updated prices back to Redis
        self.save()

        # Now add product objects to temporary cart for iteration
        for product in products:
            product_id = str(product.id)
            cart[product_id]["product"] = product

        # iterating over the raw data with string values
        # Iterate over the temporary cart with product objects
        for item in cart.values():
            # print(cart.values())
            item["price"] = Decimal(item["price"])
            # print("Before conversion", item["discounted_price"])
            # print(type(item["discounted_price"]))
            item["discounted_price"] = Decimal(item["discounted_price"])
            # print("After conversion", item["discounted_price"])
            # print(type(item["discounted_price"]))
            price_to_use = (
                item["discounted_price"]
                if item["discounted_price"] != 0
                else item["price"]
            )
            # print("Price to use", price_to_use)

            item["total_price"] = price_to_use * item["quantity"]
            yield item

    def __len__(self):
        """
        Count all items in the cart.
        """
        # quantity already converted to int by __iter__
        return sum(item["quantity"] for item in self.cart.values())

    def get_total_price(self):
        total = Decimal("0")
        # print(self.cart.values())
        for item in self.cart.values():
            # print(item)
            if item["discounted_price"] != Decimal("0"):
                total += item["discounted_price"] * item["quantity"]
            else:
                total += item["price"] * item["quantity"]

        return total

        # return sum(
        #     (
        #         item["discounted_price"] * item["quantity"]
        #         if item["discounted_price"] != Decimal("0")
        #         else item["price"] * item["quantity"]
        #     )
        #     for item in self.cart.values()
        # )

    def clear(self):
        """
        Clear the cart in Redis.
        """
        self.cart = {}  # Reset the cart in memory
        self.redis_client.delete(self.cart_key)
