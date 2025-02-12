FROM python:3.11
RUN mkdir -p /usr/src/Cooking_Book
WORKDIR /usr/src/Cooking_Book
COPY . /usr/src/Cooking_Book
COPY dump/dump-recipes.dump /docker-entrypoint-initdb.d/
RUN pip install --no-cache-dir -r requirements.txt
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

