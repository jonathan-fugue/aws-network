LWCFLAGS = --werror

default: check

rwildcard=$(wildcard $1$2) $(foreach d,$(wildcard $1*),$(call rwildcard,$d/,$2))
LUDWIG = $(call rwildcard,,*.lw)

ludwig: $(LUDWIG)

$(LUDWIG):
	lwc $(LWCFLAGS) $@ > /dev/null

check: ludwig

.PHONY: $(LUDWIG) ludwig check
