FROM ubuntu:22.10

RUN apt update
RUN apt-get install python3 -y
RUN apt-get install python3-pip -y
RUN apt install libncurses5-dev -y
RUN apt install libgdbm-dev -y
RUN apt install libnss3-dev -y
RUN apt install libssl-dev -y
RUN apt install libreadline-dev -y
RUN apt install libffi-dev -y
RUN apt install libncurses5 -y
RUN apt install lsb-core -y
RUN apt-get install 
RUN pip install ibm_db
RUN apt install libxml2 -y
RUN pip install setuptools==57
RUN pip install ifxpy
RUN pip install google-cloud-storage
RUN pip install numpy 
RUN pip install openpyxl
RUN pip install pandas
RUN pip install psycopg2-binary
RUN pip install requests
COPY requirements.txt .
RUN pip install -r requirements.txt
ENV INFORMIXDIR=/opt/IBM/Informix_Client-SDK
ENV CSDK_HOME=/opt/IBM/Informix_Client-SDK
ENV LD_LIBRARY_PATH=/opt/IBM/Informix_Client-SDK/lib/cli:/opt/IBM/Informix_Client-SDK/lib/esql:$LD_LIBRARY_PATH
COPY informix_installer/ /informix_installer
WORKDIR /informix_installer
RUN bash ./installclientsdk -i silent -r ./response.bundle -DLICENSE_ACCEPTED=TRUE
COPY sqlhosts /opt/IBM/Informix_Client-SDK/etc/
RUN rm -R /informix_installer
WORKDIR /app