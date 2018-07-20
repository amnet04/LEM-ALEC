FROM debian:9

MAINTAINER Kamil Kwiek <kamil.kwiek@continuum.io>

# Locale config
ENV LANG=C.UTF-8 LC_ALL=C.UTF-8


# Basic debian packages updates and instalation
RUN apt-get update --fix-missing && apt-get install -y apt-utils 
RUN apt-get install -y make build-essential libssl-dev zlib1g-dev
RUN apt-get install -y libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm
RUN apt-get install -y libncurses5-dev  libncursesw5-dev xz-utils tk-dev
RUN apt-get install -y wget bzip2  ca-certificates
RUN apt-get install -y libglib2.0-0 libxext6 libsm6 libxrender1
RUN apt-get install -y git mercurial subversion

# Instalación de TINI
RUN apt-get install -y curl grep sed dpkg && \
    TINI_VERSION=`curl https://github.com/krallin/tini/releases/latest | grep -o "/v.*\"" | sed 's:^..\(.*\).$:\1:'` && \
    curl -L "https://github.com/krallin/tini/releases/download/v${TINI_VERSION}/tini_${TINI_VERSION}.deb" > tini.deb && \
    dpkg -i tini.deb && \
    rm tini.deb && \
    apt-get clean

# Python 3.5 instalation
RUN apt-get install -y python3.5
RUN apt-get install -y python3.5-dev
RUN apt-get install -y python3.5-venv


# pip 3.5 instalation and simbolic link creation to
# relplace python and  pip default versions.
RUN wget https://bootstrap.pypa.io/get-pip.py
RUN python3.5 get-pip.py
RUN ln -s /usr/bin/python3.5 /usr/local/bin/python3
RUN rm /usr/local/bin/pip3
RUN ln -s /usr/local/bin/pip /usr/local/bin/pip3

# Install Jupiter notebook
RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install jupyter

# Install numpy, scipy, matplotlib, sklearn and pandas
RUN python3 -m pip install numpy
RUN python3 -m pip install scipy
RUN python3 -m pip install matplotlib
RUN python3 -m pip install scikit-learn
RUN python3 -m pip install pandas

# Install geopandas and dependencies
RUN python3 -m pip install shapely
RUN python3 -m pip install fiona
RUN python3 -m pip install six
RUN python3 -m pip install pyproj
RUN python3 -m pip install geopy
RUN python3 -m pip install rtree 
RUN python3 -m pip install geopandas

# Punto de entrada TINI
ENTRYPOINT [ "/usr/bin/tini", "--" ]

# Directorio de trabajo
WORKDIR /src

# Arrancar bash
CMD [ "/bin/bash" ]