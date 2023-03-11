FROM python:3
RUN ["apt-get", "update"]
RUN ["apt-get", "install", "-y", "vim"]
RUN ["apt-get", "install", "-y", "less"]
RUN pip install flask
RUN pip install requests
ADD web /
EXPOSE 11000
EXPOSE 3333
CMD [ "python", "./contents.py"]