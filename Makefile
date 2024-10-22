# Makefile

# Variables
VENV = flask_env
PYTHON = python3
PIP = $(VENV)/bin/pip
ACTIVATE = source $(VENV)/bin/activate

# Install Flask
install_flask: 
	$(PIP) install Flask

# Upgrade pip
upgrade_pip: install_flask
	$(PIP) install --upgrade pip

# Run the Flask app
run: upgrade_pip
	$(ACTIVATE) && python -u main.py

# Clean up virtual environment
clean:
	rm -rf $(VENV)