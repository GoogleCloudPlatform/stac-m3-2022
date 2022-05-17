PROJECT=$(shell gcloud config get-value project)
NODE_PREFIX=node

.PHONY: default all install clean run-antuco run-shasta run-kanaga ping facts reboot console inventory

default: all

all: inventory install

install:
	ansible-playbook -i hosts -e stac_m3_project_name=$(PROJECT) install.yml

clean:
	rm -f hosts

run-antuco:
	gcloud compute ssh $(NODE_PREFIX)01 --command 'sudo /m3/run/test/run-antuco.sh' -- -t

run-shasta:
	gcloud compute ssh $(NODE_PREFIX)01 --command 'sudo /m3/run/test/run-shasta.sh' -- -t

run-kanaga:
	gcloud compute ssh $(NODE_PREFIX)01 --command 'sudo /m3/run/test/run-kanaga.sh' -- -t

ping:
	ansible -i hosts -om ping stac

facts:
	ansible -i hosts -m setup stac

reboot:
	ansible -i hosts -ba reboot stac

console:
	ansible-console -i hosts -b stac

inventory:
	./genhosts.py --output-file hosts --project=$(PROJECT) $(NODE_PREFIX)
