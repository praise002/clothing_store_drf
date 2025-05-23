from rest_framework.test import APITestCase



class TestPayments(APITestCase):
    initiate_payment_flw_url = "/api/v1/payments/flw/initiate-payment/"
    initiate_payment_paystack_url = "/api/v1/payments/paystack/initialize-transaction/"
    
    def test_flw(self):
        # Test success(200)
        # Test 404(order_id does not exist)
        # Test 401
        # Test 400 or 422
        # Test payment status if pais
        pass
    
    def test_paystack(self):
        # Test success(200)
        # Test 404(order_id does not exist)
        # Test 401
        # Test 400 or 422
        # Test payment status if pais
        pass
    