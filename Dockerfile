# Use a base Python image
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements.txt (if you have one) and install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt
COPY config.json /app/config.json
COPY Main.py /app/ 

# Copy the rest of the bot's files to the container
COPY . /app/

# Run the bot script when the container starts
CMD ["python", "Main.py"]
