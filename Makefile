DIST_DIR = tensorhive/app/web/dist
CONFIG_DIR = ~/.config/TensorHive

# Global TODOs
# TODO Nice to have: make dist

all:
	make app
	make dev
	make dev-deps
	make docs
	make codestyle

app:
	$(call yellow, "Checking for existing web app build distribution...")
ifneq ($(wildcard $(DIST_DIR)),)
	$(call red, "Skipping building web app because directory $(DIST_DIR) already exists.")
else
	$(call red, "$(DIST_DIR) not found...")
	$(call green, "Building Vue.js web app...")
	(cd tensorhive/app/web/dev && npm install && npm run build)
endif
	$(call green, "Done.\n")

dev:
	@echo "Installing TensorHive in editable package mode..."
	pip install --quiet --editable .
	$(call green, "Done.\n")

dev-deps:
	@echo "Installing additinal dependencies for development/testing..."
	pip install -r requirements-dev.txt
	$(call green, "Done.\n")


clean-config:
	$(call yellow, "Cleaning existing configuration files...")
ifneq ($(wildcard $(CONFIG_DIR)),)
	- cd $(CONFIG_DIR) && rm *.ini
	$(call green, "Done.\n")
else
	@echo "$(CONFIG_DIR) does not exist, continuing...\n"
endif

clean:
	$(call red, "1. Removing web app build artifacts...")
	rm --recursive --force $(DIST_DIR)
	$(call green, "Done.\n")

	$(call red, "2. Uninstalling TensorHive...")
	pip uninstall --yes tensorhive
	$(call green, "Done.\n")

	$(call red, "3. Removing docs...")
	rm --recursive --force docs
	$(call green, "Done.\n")


codestyle:
	- mypy -p tensorhive -p tests
	@echo "-------------------------------------------"
	python -m flake8 tensorhive tests

define red
	@tput setaf 1
	@echo $1
	@tput sgr0
endef

define green
	@tput setaf 2
	@echo $1
	@tput sgr0
endef

define yellow
	@tput setaf 3
	@echo $1
	@tput sgr0
endef

.PHONY: all
