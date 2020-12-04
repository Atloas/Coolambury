PYTHON = python3
SERVER_APP := $(shell pwd)/Server/src/app.py
CLIENT_APP := $(shell pwd)/Client/src/runClient.py
COMMON_PATH := $(shell pwd)/Common/
SET_PYTHONPATH := PYTHONPATH='.'

server: .FORCE
	$(SET_PYTHONPATH) $(PYTHON) $(SERVER_APP)

client: .FORCE
	$(SET_PYTHONPATH) $(PYTHON) $(CLIENT_APP)

.PHONY: .FORCE
FORCE:
