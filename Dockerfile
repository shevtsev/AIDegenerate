FROM python:3.12

WORKDIR /apps

COPY . .
RUN pip install --no-cache-dir -r requirements.txt

CMD python AI_degenerate_bot/main.py & python AI_degenerate_bot/ChannelProccessing.py