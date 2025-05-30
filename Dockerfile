# Base image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install dependencies
RUN apt-get update \
    && apt-get install -y gcc libpq-dev netcat-openbsd libglib2.0-0 \
    && apt-get install -y libpango-1.0-0 libcairo2 libgdk-pixbuf2.0-0 libffi-dev libpango1.0-dev libcairo2-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* 


# Set the working directory in the container
WORKDIR /app

# Install dependencies
RUN pip install --upgrade pip

# Copy the requirements file to the app dir app/requirements.txt
COPY requirements.txt . 

# Install dependencies
# RUN pip install -r requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Now copy the rest of the application files
COPY . .

# Make scripts executable
RUN chmod +x entrypoint.sh wait-for-it.sh

# Set the entrypoint
ENTRYPOINT ["./entrypoint.sh"]