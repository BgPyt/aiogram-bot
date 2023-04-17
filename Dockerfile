FROM python:3
COPY . /usr/src/app
WORKDIR /usr/src/app
RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt
CMD ["python", "main.py"]