.PHONY: default apply destroy data clean

default: apply

.terraform:
	terraform init

apply: .terraform
	terraform apply

destroy: .terraform
	terraform destroy

data: .terraform
	terraform apply \
		-var name=data \
		-var instance_count=1 \
		-var boot_disk_type=pd-ssd \
		-var boot_disk_size=65536

clean:
	rm -rf .terraform .terraform.lock.hcl terraform.tfstate terraform.tfstate.backup
