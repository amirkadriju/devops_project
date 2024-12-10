# Start from a minimal Python 3.11 image
FROM python:3.11-slim

# Define the working directory in the container
WORKDIR /code

# Copy the requirements file into the container
COPY ./requirements.txt /code/requirements.txt

# Install the dependencies
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copy all source code from the "server" folder into the container
COPY ./server /code/server

# Extend the Python path to ensure modules are found
ENV PYTHONPATH="$PYTHONPATH:/code"

# Expose port 8080 to allow access to the FastAPI app
EXPOSE 8080

# Start the FastAPI server using uvicorn
CMD ["uvicorn", "server.py.main:app", "--host", "0.0.0.0", "--port", "8080"]
