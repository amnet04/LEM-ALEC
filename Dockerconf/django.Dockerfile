FROM debian:8.5

MAINTAINER Kamil Kwiek <kamil.kwiek@continuum.io>

ENV LANG=C.UTF-8 LC_ALL=C.UTF-8

RUN apt-get update --fix-missing && apt-get install -y apt-utils && \
    apt-get install -y wget bzip2  ca-certificates \
    libglib2.0-0 libxext6 libsm6 libxrender1 \
    git mercurial subversion

RUN echo 'export PATH=/opt/conda/bin:$PATH' > /etc/profile.d/conda.sh && \
    wget --quiet https://repo.continuum.io/archive/Anaconda3-4.2.0-Linux-x86_64.sh -O ~/anaconda.sh && \
    /bin/bash ~/anaconda.sh -b -p /opt/conda && \
    rm ~/anaconda.sh

RUN apt-get install -y curl grep sed dpkg && \
    TINI_VERSION=`curl https://github.com/krallin/tini/releases/latest | grep -o "/v.*\"" | sed 's:^..\(.*\).$:\1:'` && \
    curl -L "https://github.com/krallin/tini/releases/download/v${TINI_VERSION}/tini_${TINI_VERSION}.deb" > tini.deb && \
    dpkg -i tini.deb && \
    rm tini.deb && \
    apt-get clean

# Librerías para que sirva opencv
RUN apt-get install -y libgtk2.0-dev libpng12-0 binutils libproj-dev tesseract-ocr tesseract-ocr-spa tesseract-ocr-spa tesseract-ocr-fra 

#Crear y activar el enviroment root en conda
RUN bash -c "source /opt/conda/bin/activate root"

# Opencv
RUN /opt/conda/bin/conda install -y --quiet -c menpo opencv3=3.2.0

RUN /opt/conda/bin/conda install -y --quiet -c conda-forge psycopg2=2.7.1 && \
    /opt/conda/bin/conda install -y --quiet -c r r-essentials=1.6.0 && \
    /opt/conda/bin/conda install -y --quiet -c anaconda-nb-extensions nbbrowserpdf && \
    /opt/conda/bin/conda install -y --quiet -c anaconda basemap && \
    /opt/conda/bin/conda install -y --quiet -c anaconda openpyxl 


ENV PATH /opt/conda/bin:$PATH
ENV GDAL_DATA /opt/conda/share/gdal
ENV GOOGLE_APPLICATION_CREDENTIALS=/src/Auth/secret.json

ENTRYPOINT [ "/usr/bin/tini", "--" ]

WORKDIR /src

CMD [ "/bin/bash" ]
