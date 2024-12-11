# Use the official Python image from Docker Hub
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements.txt file into the container
COPY requirements.txt /app/

# Create a virtual environment inside the container
RUN python -m venv venv

# Install the dependencies into the virtual environment
RUN ./venv/bin/pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code into the container
COPY . /app

# Set the environment to use the virtual environment's Python
ENV PATH="/app/venv/bin:$PATH"

# Define the default command to run your application (e.g., app.py)
CMD ["python", "queryEnphaseGateway.py"]

