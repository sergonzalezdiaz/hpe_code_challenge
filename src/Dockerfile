FROM python:3.9-slim

# Create workdir
WORKDIR /code

# Copy dependencies
COPY ./src/requirements.txt /code/requirements.txt

# Install the dependencies
RUN pip install --upgrade pip
RUN pip install -r /code/requirements.txt

# Copy the files
COPY ./src /code
COPY .env /code/

# Start the service
CMD ["uvicorn", "app.main:app", "--proxy-headers", "--host", "0.0.0.0", "--port", "80"]
