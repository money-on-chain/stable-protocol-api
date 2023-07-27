FROM python:3.10

LABEL maintainer='martin.mulone@moneyonchain.com'

ENV PYTHONUNBUFFERED 1

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir /home/app

WORKDIR /home/app/
COPY api/ ./api/

ENV PATH "$PATH:/home/app/"

ENV PYTHONPATH "${PYTONPATH}:/home/app/"

CMD ["uvicorn", "api.app:app", "--host", "0.0.0.0", "--port", "5005"]

EXPOSE 5005