# 🛍️ Clothing Store API

![Django Tests](https://github.com/praise002/clothing_store_drf/actions/workflows/django-tests.yml/badge.svg)

A comprehensive e-commerce REST API built with Django Rest Framework, featuring a complete clothing store backend with user authentication, product management, shopping cart, order processing, and payment integration.

## ✨ Features

- 🔐 **User Authentication & Registration** - Secure user management with JWT tokens
- 📦 **Product Management** - Complete CRUD operations for products
- 🛒 **Shopping Cart** - Add, remove, and manage cart items
- ❤️ **Wishlist** - Save favorite products for later
- 📋 **Order Management** - Full order lifecycle from creation to fulfillment
- 🎫 **Coupons & Discounts** - Flexible discount system
- 👤 **User Profiles** - Customizable user profiles and preferences
- ⭐ **Reviews & Ratings** - Product review and rating system
- 🎛️ **Admin Dashboard** - Comprehensive admin interface

## 🛠️ Tech Stack

- **Backend Framework:** Django Rest Framework (DRF)
- **Database:** PostgreSQL
- **Containerization:** Docker & Docker Compose
- **Task Queue:** Celery with Redis broker
- **Payment Gateway:** Paystack integration
- **Testing:** Django Test Framework
## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- PostgreSQL
- Redis (for Celery tasks)
- Docker (optional)

### 📋 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/praise002/clothing_store_drf.git
   cd clothing_store_drf
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv env
   source env/bin/activate  # On Windows: env\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
   Or using make:
   ```bash
   make reqn
   ```

4. **Environment setup**
   - Create a `.env` file in the root directory
   - Copy contents from `.env.example` and set your values
   - Create a PostgreSQL database (using PG Admin GUI or psql CLI)

5. **Database migrations**
   ```bash
   python manage.py migrate
   ```
   Or using make:
   ```bash
   make mig
   ```

## 🏃‍♂️ Running the Application

### Local Development

1. **Start the Django server**
   ```bash
   python manage.py runserver
   ```
   Or using make:
   ```bash
   make serv
   ```

2. **Start Redis (Windows)**
   ```bash
   docker run -it --rm --name redis -p 6379:6379 redis
   ```

3. **Start Celery worker**
   ```bash
   celery -A clothing_store worker -l info --pool=solo
   ```

4. **Start Celery beat scheduler**
   ```bash
   celery -A clothing_store beat -l info
   ```

5. **Start Flower monitoring (optional)**
   ```bash
   celery -A clothing_store flower --basic-auth=admin:password
   ```

### Docker Deployment

**Option 1: Docker Compose**
```bash
docker-compose up
```

**Option 2: Using Make**
```bash
make up
```

### Ngrok Setup (for Paystack webhooks)

```bash
ngrok http 8000
```

## 🧪 Testing

Run the test suite:
```bash
python manage.py test apps.app_name.tests
```

## 📝 Important Notes

### Paystack Webhook Setup
- For webhooks to work with Paystack, install ngrok using Chocolatey
- Ensure Chocolatey is installed on your system
- Follow the installation guide in the resources section

### Windows Makefile Usage
To use the makefile on Windows:
1. Run PowerShell as administrator
2. Visit the [Chocolatey website](https://chocolatey.org/)
3. Install make: `choco install make`
4. You can now use make commands in your Django app

## 🔗 Resources & References

### Development & Deployment
- [Ngrok Download](https://download.ngrok.com/downloads/windows)
- [Docker Best Practices](https://testdriven.io/blog/docker-best-practices/)
- [Production Django Deployments on Heroku](https://testdriven.io/blog/production-django-deployments-on-heroku/)
- [Dockerizing Celery and Django](https://testdriven.io/courses/django-celery/docker/)
- [Dockerizing Django with Postgres, Gunicorn, and Nginx](https://testdriven.io/blog/dockerizing-django-with-postgres-gunicorn-and-nginx/#project-setup)

### Deployment Guides
- [Deploying Django to Production](https://developer.mozilla.org/en-US/docs/Learn_web_development/Extensions/Server-side/Django/Deployment#example_hosting_on_railway)
- [Deploy Django on Railway](https://www.codingforentrepreneurs.com/blog/deploy-django-on-railway-with-this-dockerfile)
- [Railway Variables Documentation](https://docs.railway.com/reference/variables)

### Payment Integration
- [Integrating Paystack Payment Gateway - Part I](https://willingly.hashnode.dev/integrating-paystack-payment-gateway-with-django)
- [Integrating Paystack Payment Gateway - Part II](https://willingly.hashnode.dev/integrating-paystack-payment-gateway-with-django-ii)

### Security & OAuth
- [An Opinionated Guide to DRF OAuth](https://www.circumeo.io/blog/entry/an-opinionated-guide-to-drf-oauth/)
- [API Security Scanner](https://www.apisec.ai/blog/apisec-the-only-platform-for-automated-api-security-testing)

## 📸 Screenshots

### Application Interface
<div align="center">
<img src="./static/media/home1.png" alt="Home Page" width="45%" style="margin: 10px;">
<img src="./static/media/auth.png" alt="Authentication" width="45%" style="margin: 10px;">
<img src="./static/media/cart.png" alt="Shopping Cart" width="45%" style="margin: 10px;">
<img src="./static/media/shop.png" alt="Shop Page" width="45%" style="margin: 10px;">
<img src="./static/media/ghop.png" alt="Product Gallery" width="45%" style="margin: 10px;">
<img src="./static/media/rp.png" alt="Product Reviews" width="45%" style="margin: 10px;">
<img src="./static/media/shipping.png" alt="Shipping Info" width="45%" style="margin: 10px;">
</div>

### Admin Dashboard
<div align="center">
<img src="./static/media/admin1.png" alt="Admin Dashboard 1" width="30%" style="margin: 10px;">
<img src="./static/media/admin2.png" alt="Admin Dashboard 2" width="30%" style="margin: 10px;">
<img src="./static/media/admin3.png" alt="Admin Dashboard 3" width="30%" style="margin: 10px;">
</div>

