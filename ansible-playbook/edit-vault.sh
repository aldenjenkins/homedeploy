#!/bin/bash
EDITOR=kak ansible-vault edit --vault-password-file=./vault-password group_vars/all/vault.yml
