.PHONY: default deploy clean results list ssh antuco shasta kanaga data

default: deploy

deploy:
	make -C terraform
	make -C ansible

clean:
	make -C ansible clean
	make -C terraform destroy

results:
	make -C results

list:
	gcloud compute instances list

ssh:
	gcloud compute ssh node01

antuco: deploy
	make -C ansible run-antuco
	make -C results

shasta: deploy
	make -C ansible run-shasta
	make -C results

kanaga: deploy
	make -C ansible run-kanaga
	make -C results

data:
	make -C terraform data
	make -C ansible NODE_PREFIX=data
