LWCFLAGS = --werror

default: check

LUDWIG = $(wildcard **/*.lw)

ludwig: $(LUDWIG)

$(LUDWIG):
	lwc $(LWCFLAGS) $@ > /dev/null

check: ludwig

.PHONY: $(LUDWIG) ludwig check
