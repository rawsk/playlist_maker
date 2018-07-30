# Playlist Maker

## Environment
- Amazon Linux 2

## User Data
```
yum update -y
yum install git gcc python3-devel -y
amazon-linux-extras install nginx1.12 -y
```

## Set Up
```
git clone https://github.com/rawsk/playlist_maker.git
cd playlist_maker/
python3 -m venv venv
venv/bin/pip install -r requirements.txt
```