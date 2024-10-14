FROM python:3.12.4

WORKDIR /app

COPY project/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY /project/* .

EXPOSE 8000

CMD ["uvicorn", "project.main:app", "--host", "0.0.0.0", "--port", "8000"]