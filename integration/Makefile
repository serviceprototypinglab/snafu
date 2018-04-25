all:
	@echo You need to run 'make install/test/apbtest/helmtest' explicitly.

install:
	sudo cp snafu.service /etc/systemd/system/
	systemctl status snafu.service

test:
	ansible-playbook playbooks/snafu-playbook.yaml

apbtest:
	cp playbooks/snafu-playbook.yaml playbooks/provision.yml
	apb prepare

helmtest:
	helm install --dry-run --debug snafu-helmchart
