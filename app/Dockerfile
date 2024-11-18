FROM python:3.9

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

# Run Gunicorn with the --reload flag for development (auto-reload on file changes)
CMD ["gunicorn", "--bind", "0.0.0.0:5001", "--reload", "main:app"]
