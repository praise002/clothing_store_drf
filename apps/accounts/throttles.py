from rest_framework.throttling import ScopedRateThrottle

class EmailThrottle(ScopedRateThrottle):

    def get_cache_key(self, request, view):
        # Extract email from request data
        email = request.data.get('email')  #TODO: FIX
        
        if not email:
            # Skip throttling if email is not provided
            return None

        # print(self.scope)
        # print(f'email-throttle-{email}')
        # Generate a unique cache key using the email
        return self.cache_format % {
            'scope': self.scope,
            'ident': f'email-throttle-{email}'
        }