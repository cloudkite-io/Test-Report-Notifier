FROM python:3.8.6

WORKDIR usr/local/e2e-test

# install script dependencies
RUN pip3 install requests
RUN pip3 install google-cloud-storage

# copy e2e-test report script to docker container
COPY e2e.py /usr/local/bin/e2e-report

# make script executable
RUN chmod a+x /usr/local/bin/e2e-report

# set script as entrypoint
ENTRYPOINT ["e2e-report"]
