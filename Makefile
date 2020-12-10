PYTHON = python3
SERVER_APP := $(shell pwd)/Server/src/server.py
CLIENT_APP := $(shell pwd)/Client/src/runClient.py
CONFIG_PATH = $(shell pwd)/config.json
SET_PYTHONPATH := PYTHONPATH='.'

server: .FORCE
	$(SET_PYTHONPATH) $(PYTHON) $(SERVER_APP) $(CONFIG_PATH)

client: .FORCE
	$(SET_PYTHONPATH) $(PYTHON) $(CLIENT_APP) $(CONFIG_PATH)

.PHONY: .FORCE
FORCE:
