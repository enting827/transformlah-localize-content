# Use a slim Python image for a smaller final image size
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file and install dependencies
# This is a separate layer to leverage Docker's build cache.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code
COPY . .

# Expose the port your FastAPI application listens on
EXPOSE 8000

# The command to run your application using Uvicorn
# The command references the correct file path within the container (/app/main.py)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
