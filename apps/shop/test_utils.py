from apps.common.utils import TestUtil
from apps.orders.models.order import Order, OrderItem
from apps.shop.models import Category, Product, Review


class TestShopUtil:

    def category():
        category1, _ = Category.objects.get_or_create(name="Men")
        category2, _ = Category.objects.get_or_create(name="Women")
        return category1, category2

    def product():
        category1, category2 = TestShopUtil.category()
        user1 = TestUtil.verified_user()

        product1, _ = Product.objects.get_or_create(
            name="Test Product 1",
            description="This is test product 1",
            price=1000,
            in_stock=10,
            category=category1,
            image="",
        )

        product2, _ = Product.objects.get_or_create(
            name="Test Product 2",
            description="This is test product 2",
            price=2000,
            in_stock=0,  # Out of stock
            category=category2,
            image="",
        )

        product3, _ = Product.objects.get_or_create(
            name="Test Product 3",
            description="This is test product 3",
            price=2000,
            in_stock=50,
            image="",
        )

        Review.objects.get_or_create(
            product=product3,
            customer=user1.profile,
            text="Initial review text",
            rating=3,
        )

        return product1, product2, product3

    def review():
        _, _, product3 = TestShopUtil.product()
        user1 = TestUtil.verified_user()
        review, _ = Review.objects.get_or_create(
            product=product3,
            customer=user1.profile,
            text="Initial review text",
            rating=4,
        )
        return review

    def order_item_for_review(product, customer):
        order, _ = Order.objects.get_or_create(
            customer=customer, shipping_status="delivered"
        )
        item, _ = OrderItem.objects.get_or_create(
            order=order, product=product, quantity=1, price=product.price
        )
        return item
