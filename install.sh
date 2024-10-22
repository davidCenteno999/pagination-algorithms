
#!/bin/bash

sudo dnf update -y
sudo dnf install -y python3 python3-pip

pip3 install --user virtualenv

python3 -m venv flask_env

source flask_env/bin/activate

make

python -u app.py