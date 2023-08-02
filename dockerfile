FROM selenium/standalone-firefox:4.11.0-20230801

RUN sudo apt-get update
RUN sudo apt-get upgrade -y
RUN sudo apt-get install python3-pip -y
RUN sudo apt-get install git -y
ENV BOT_API_KEY=placeholder
RUN sudo mkdir /app
RUN cd app
WORKDIR /app
RUN sudo git clone https://github.com/Discobrick/Telegram-reel-and-tiktok-download-bot
WORKDIR /app/Telegram-reel-and-tiktok-download-bot
RUN pip3 install python-telegram-bot==20.3
RUN pip3 install selenium==4.10.0
RUN pip3 install webdriver_manager==3.8.6


