# Clothing store

# Features
* User Authentication and Registration
* Product Management
* Shopping Cart
* Wishlist
* Order Management
* Coupons
* Discounts
* User Profiles
* Reviews and Ratings
* Admin Dashboard

# Tech Stack
* Django Rest Framework
* Postgres
* Docker
* Celery & Redis for asynchronous tasks
  
# How to run locally
* Download this repo or run: 
```bash
    $ git clone repo
```

#### In the root directory:
- Create and activate a virtual environment
- Install all dependencies
```bash
    $ pip install -r requirements.txt
```
- Create an `.env` file and copy the contents from the `.env.example` to the file and set the respective values. A postgres database can be created with PG ADMIN or psql

- Run Locally
```bash
    $ python manage.py migrate
```
```bash
    $ python manage.py runserver
```
```bash
    $ python manage.py test apps.app_name.tests
```

**On windows**
```bash
    $ docker run -it --rm --name redis -p 6379:6379 redis
```
```bash
    $ celery -A clothing_store worker -l info --pool=solo
```
```bash
    $ celery -A clothing_store beat -l info
```
```bash
    $ celery -A clothing_store flower --basic-auth=admin:password
```

- Run With Docker
```bash
    $ docker-compose up  
```
```bash
    $ docker compose exec web python manage.py migrate
```
```bash
    $ docker compose exec web python manage.py createsuperuser
```
```bash
    $ docker-compose exec web python manage.py collectstatic
```

- Run with ngrok
 ```bash
    $   ngrok http 8000
```

## NOTE
* For webhook to work with paystack install ngrok with choco. Follow the installation guide in the resources section. Ensure choco is installed on your system.

## Resources 
* [Ngrok](https://download.ngrok.com/downloads/windows)
* [Integrating Paystack Payment Gateway Into Your Django Project - Part I](https://willingly.hashnode.dev/integrating-paystack-payment-gateway-with-django)
* [Integrating Paystack Payment Gateway Into Your Django Project - Part II](https://willingly.hashnode.dev/integrating-paystack-payment-gateway-with-django-ii)
* [An opinionated guide to drf-oauth](https://www.circumeo.io/blog/entry/an-opinionated-guide-to-drf-oauth/)

  
# Home Page
<img src="./static/media/home1.png"> 
<img src="./static/media/auth.png"> 
<img src="./static/media/cart.png"> 
<img src="./static/media/shop.png"> 
<img src="./static/media/ghop.png"> 
<img src="./static/media/rp.png"> 
<img src="./static/media/shipping.png"> 


 

# Admin dashboard
<img src="./static/media/admin1.png">  
<img src="./static/media/admin2.png">  
<img src="./static/media/admin3.png">  
 
 

