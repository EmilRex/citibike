FROM python:3.6.5

WORKDIR /opt/citibike

COPY . /opt/citibike

RUN make install

CMD ["make", "run"]