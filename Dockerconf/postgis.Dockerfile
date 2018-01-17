FROM sameersbn/postgresql:9.6-2

RUN wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add - && \
    apt-get -y update -qq && \
    sudo apt-get install -y postgresql-9.6-postgis-2.3 && \
    sudo apt-get install -y postgresql-9.6-postgis-2.3-scripts && \
    sudo apt-get install -y postgresql-9.6-pgrouting