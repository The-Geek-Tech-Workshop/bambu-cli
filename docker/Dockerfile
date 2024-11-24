ARG VERSION

FROM python:3.12-slim

ARG VERSION
RUN pip install --no-cache-dir bambu-cli==${VERSION}

ENTRYPOINT ["bambu"]