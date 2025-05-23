FROM python:3.11-slim

WORKDIR /app


# Copy app files
COPY app/ /app
COPY wheelhouse/ ./wheelhouse/
RUN pip install --no-index --find-links=wheelhouse -r requirements.txt

# Set environment variables for Flask
ENV FLASK_APP=main.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_ENV=development

EXPOSE 5000

# Use Flask CLI to run the app
CMD ["flask", "run"]
