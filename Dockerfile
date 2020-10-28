FROM python:3.8.6

WORKDIR usr/local/test_notifier

# install script dependencies
RUN pip3 install requests
RUN pip3 install google-cloud-storage

# copy test_notifier script to docker container
COPY test_notifier.py /usr/local/bin/test_notifier

# make script executable
RUN chmod a+x /usr/local/bin/test_notifier

# set script as entrypoint
ENTRYPOINT ["test_notifier"]
