#NS=`oc config get-contexts | grep ^* | awk '{print $5}'`
NS=`grep ^current-context ~/.kube/config | cut -d ":" -f 2 | cut -d "/" -f 1 | tr -d " "`

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
	helm lint snafu-chart
	helm init --tiller-namespace $(NS)
	helm install --dry-run --debug --tiller-namespace $(NS) snafu-chart
