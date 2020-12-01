# set base image (host OS)
FROM python:3.8

# set the working directory in the container
WORKDIR /code

ENV VIRTUAL_ENV=/opt/venv
RUN python -m venv /opt/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
EXPOSE 5000
# copy the dependencies file to the working directory
COPY requirements.txt .

# install dependencies
RUN . /opt/venv/bin/activate && pip install -r requirements.txt && pip install gunicorn

# copy the content of the local src directory to the working directory
COPY flaskr/ .

# command to run on container start
CMD ["gunicorn"  , "--bind", "0.0.0.0:5000", "flaskr:create_app()"]