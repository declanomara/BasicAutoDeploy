#!/usr/bin/env bash

sudo pip3 install -r requirements.txt

sudo cp basicautodeploy.service /lib/systemd/system/
mkdir /usr/share/BasicAutoDeploy
sudo cp -r * /usr/share/BasicAutoDeploy/


sudo systemctl daemon-reload

sudo systemctl restart basicautodeploy.service

sudo systemctl enable basicautodeploy.service