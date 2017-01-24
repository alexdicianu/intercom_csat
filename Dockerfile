# ======================================
# Run command: 
# $ docker run -t -i --name csat_request \
#  -e SENDGRID_API_KEY='xxxxxxxxxxxxxxxxxxxxxxxxxxx' \
#  -v /Users/dicix/work/pantheon/csat:/opt/csat_request dicix/csat
# ======================================

FROM ubuntu:16.04
MAINTAINER alex dicianu "alex.dicianu@gmail.com"
RUN apt-get update

# Install basic applications
RUN apt-get install -y vim curl wget build-essential python-software-properties tar git curl nano wget dialog net-tools 

# Install Python and Basic Python Tools
RUN apt-get install -y python python-dev python-distribute python-pip

#ADD csat_request.py /opt/

WORKDIR /opt/csat_request/

RUN pip install sendgrid

CMD python /opt/csat_request/csat_request.py