FROM python:3

WORKDIR /interface

COPY interface/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY interface/ .

CMD [ "python", "./receiver.py" ]