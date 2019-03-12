FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY bitcoinsv-explorer-bot.py .

CMD [ "python", "./bitcoinsv-explorer-bot.py" ]
