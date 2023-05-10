# Make sure we have ansible_collections/servicenow/itsm as a prefix. This is
# ugly as hack, but it works. I suggest all future developer to treat next few
# lines as an opportunity to learn a thing or two about GNU make ;)
collection := $(notdir $(realpath $(CURDIR)      ))
namespace  := $(notdir $(realpath $(CURDIR)/..   ))
toplevel   := $(notdir $(realpath $(CURDIR)/../..))

err_msg := Place collection at <WHATEVER>/ansible_collections/maas/maas
ifeq (true,$(CI))
  $(info Running in CI setting, skipping directory checks.)
else ifneq (maas, $(collection))
  $(error $(err_msg))
else ifneq (maas, $(namespace))
  $(error $(err_msg))
else ifneq (ansible_collections, $(toplevel))
  $(error $(err_msg))
endif

python_version := $(shell \
  python -c 'import sys; print(".".join(map(str, sys.version_info[:2])))' \
)

unit_test_targets := $(shell find tests/unit -name '*.py')
integration_test_targets := $(shell ls tests/integration/targets)


.PHONY: help
help:
	@echo Available targets:
	@fgrep "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sort

# Developer convenience targets

.PHONY: clean
clean:  ## Remove all auto-generated files
	rm -rf tests/output

.PHONY: $(integration_test_targets)
$(integration_test_targets):
	ansible-test integration --requirements --python $(python_version) --diff $@

.PHONY: integration
integration:  ## Run integration tests
	ansible-test integration --docker --diff

.PHONY: integration-local
integration-local:
	ansible-test integration --local --diff
