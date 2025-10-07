# INFO! dev сборка
FROM python:3.12.11

ENV PYTHONUNBUFFERED=1

WORKDIR /site

RUN touch .env.init
COPY . .

RUN pip install --no-cache-dir -e .

CMD ["sh", "-c", "cd real_estate_agency_deals_site \
                     && python manage.py makemigrations \
                     && python manage.py migrate \
                     && python manage.py runserver 0.0.0.0:8080"]
