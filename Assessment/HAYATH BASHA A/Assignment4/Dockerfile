#
FROM  python:2.7

WORKDIR /main

COPY . /main

RUN pip install -r requirements.txt 

EXPOSE 5000

CMD python ./app.py