PYTHON = python3
SERVER_APP := $(shell pwd)/Server/src/app.py
CLIENT_APP := $(shell pwd)/Client/src/app.py
COMMON_PATH := $(shell pwd)/Common/


server: .FORCE
	$(PYTHON) $(SERVER_APP)

client: .FORCE
	$(PYTHON) $(CLIENT_APP)

.PHONY: .FORCE
FORCE:
