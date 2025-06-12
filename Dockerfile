# Use an official Python runtime as a parent image
FROM python:3.9-slim-buster

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

# Make port 5000 available to the world outside this container
EXPOSE 8260

# Define environment variable
ENV FLASK_APP=main.py

# Run app.py when the container launches
CMD gunicorn --worker-class eventlet -w 1 main:app --bind=localhost:8260