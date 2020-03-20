#!/bin/bash

ansible-playbook \
	--inventory-file hosts \
	--user root \
	--vault-id ./vault-password \
	"$@" \
	homelab.yaml
