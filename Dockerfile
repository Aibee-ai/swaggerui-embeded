FROM python:3.9

COPY requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt --index https://pypi.doubanio.com/simple
EXPOSE 8501
COPY app.py /app/app.py

WORKDIR /app
ENTRYPOINT ["streamlit", "run"]
CMD ["app.py"]