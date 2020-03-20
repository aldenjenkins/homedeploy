#!/bin/sh -x

# Namespaces:
for NAME in infra cert-manager external-dns
do
    (kubectl get namespaces | awk '{print $1}' | grep -E "^$NAME$") || kubectl create namespace $NAME
done

# Cert-manager CRDs:
kubectl apply --validate=false -f https://github.com/jetstack/cert-manager/releases/download/v0.14.0/cert-manager.crds.yaml

# Storage labels
STORAGE=rocksteady
kubectl label --overwrite nodes $STORAGE storagetype=attached
for node in $(kubectl get nodes -o json | jq -r '.items[].metadata.name' | grep -v $STORAGE)
do
    kubectl label --overwrite nodes $node storagetype=nfs
done
kubectl label --overwrite nodes krang storagetype=none
