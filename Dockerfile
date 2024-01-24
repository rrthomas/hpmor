# syntax=docker/dockerfile:1

# base image
FROM ubuntu:22.04

# set timezone
ENV TZ=Europe/Berlin

# prevent keyboard input requests in apt install
ARG DEBIAN_FRONTEND=noninteractive

# install core packages
RUN apt-get update
RUN apt-get install -y python3 git

# for pdf, copied from scripts/install_requirements_pdf.sh
RUN apt-get install -y texlive-xetex texlive-lang-german latexmk
# for ebook, copied from scripts/install_requirements_ebook.sh
RUN apt-get install -y texlive-extra-utils pandoc calibre imagemagick ghostscript

# set working directory
WORKDIR /app

# mount host directory as volume
VOLUME /app

# default command: build 1-vol pdf and all ebook formats
CMD latexmk hpmor ; ./scripts/make_ebooks.sh

# build/update image via
# docker build -t hpmor .

# run default commands (see above) via
# docker run -it --mount type=bind,src="$(pwd)",dst=/app hpmor

# run specific command or script
# docker run -it --mount type=bind,src="$(pwd)",dst=/app hpmor latexmk hpmor-1
# docker run -it --mount type=bind,src="$(pwd)",dst=/app hpmor ./scripts/make_ebooks.sh

# login via
# docker run -it --mount type=bind,src="$(pwd)",dst=/app hpmor bash
