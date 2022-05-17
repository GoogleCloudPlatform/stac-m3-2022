.PHONY: default code deploy all clean

default: all

all: deploy

code:
	make -C code

deploy: code
	make -C automation

clean:
	make -C code clean
	make -C automation clean
