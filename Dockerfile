#FROM alpine
FROM python:3.9
#RUN /usr/bin/python3 -m pip install --upgrade pip

COPY requirements.txt /app/requirements.txt
RUN /usr/local/bin/python -m pip install --upgrade pip
RUN pip3 install -r /app/requirements.txt

COPY ./ /app

RUN rm -rf /var/cache/* 
RUN rm -rf /root/.cache/* 

ENV UID=1000
ENV GID=1000
#RUN addgroup -g ${GID} -S appgroup && adduser -u ${UID} -S appuser -G appgroup
#USER appuser

ENTRYPOINT [ "python3", "-u", "/app/main.py"]

LABEL maintainer=darren.watt@gmail.com
