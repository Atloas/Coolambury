PYTHON = python3
SERVER_APP := $(shell pwd)/Server/src/app.py
CLIENT_APP := $(shell pwd)/Client/src/Communication/app.py
CLIENT_APP_WINDOW := $(shell pwd)/Client/src/runClient.py
COMMON_PATH := $(shell pwd)/Common/

server: .FORCE
	$(PYTHON) $(SERVER_APP)

client: .FORCE
	$(PYTHON) $(CLIENT_APP)

client_window: .FORCE
	$(PYTHON) $(CLIENT_APP_WINDOW)


.PHONY: .FORCE
FORCE:
