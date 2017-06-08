LWCFLAGS = --werror

default: check

ifneq ($(OS),Windows_NT)
LUDWIG = $(shell find . -name deps -prune -o -name '*.lw' -print)
endif

ifeq ($(OS),Windows_NT)
LUDWIG = $(dir /s/b '*.lw')
endif

ludwig: $(LUDWIG)

$(LUDWIG):
	lwc $(LWCFLAGS) $@ > /dev/null

check: ludwig

.PHONY: $(LUDWIG) ludwig check
