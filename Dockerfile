FROM python:3.13-slim

RUN apt-get update && \
apt-get install -y zip && \
pip install uv


COPY pyproject.toml uv.lock ./
RUN uv pip install --system -r pyproject.toml
WORKDIR /app/src

EXPOSE 8000

CMD ["python", "server.py", "-l"]
