# 1. base image
FROM python:3.12-slim

# 2. set working directory inside container
WORKDIR /app

# 3. copy requirements first (better caching)
COPY requirements.txt .

# 4. install python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 5. copy application code
COPY app.py .

# 6. expose the port flask runs on
EXPOSE 5000

# 7. start the flask app
CMD ["python", "app.py"]

