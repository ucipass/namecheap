FROM python:3.9.10-alpine

WORKDIR /namecheap

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY namecheap.py .

CMD [ "python", "/namecheap/namecheap.py" ]