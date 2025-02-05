FROM ubuntu:latest
LABEL authors="bogdanprihodko"

ENTRYPOINT ["top", "-b"]