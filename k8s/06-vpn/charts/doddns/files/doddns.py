#!/bin/env python3

import requests
import logging
import json
import os
import argparse


logging.basicConfig(level=logging.DEBUG)

DIGITAL_OCEAN_API_ROOT = 'https://api.digitalocean.com/v2/'


def get_public_ip():
    content = requests.get('http://checkip.dyndns.org', timeout=10).text
    return content.split()[-1].split('<')[0]


class ApiError(RuntimeError):
    def __init__(self, response):
        super(ApiError, self).__init__('[%(id)s] %(message)s' % response)


class DigitalOceanApi(object):
    def __init__(self, api_key):
        self._api_key = api_key

    def api_call(self, method, path, params=None, data=None):
        req = requests.request(
            method=method,
            url=DIGITAL_OCEAN_API_ROOT + path,
            headers={
                'Content-Type': 'application/json',
                'Authorization': 'Bearer %s' % (self._api_key,),
            },
            params=params,
            data=json.dumps(data),
            timeout=10,
        )

        return req.json()

    def get_record(self, domain, name):
        response = self.api_call(
            'GET',
            'domains/%(domain)s/records' % {'domain': domain}
        )
        if 'domain_records' not in response:
            raise ApiError(response)

        for record in response['domain_records']:
            if record['type'] != 'A':
                continue

            if record['name'] == name:
                return record

    def create_record(self, domain, name, data, ttl=60):
        response = self.api_call(
            'POST',
            'domains/%s/records' % (domain),
            data={
                'type': 'A',
                'name': name,
                'data': data,
                'priority': None,
                'port': None,
                'weight': None,
                'ttl': 60,
            })

        if 'domain_record' not in response:
            raise ApiError(response)

        return response

    def update_record(self, domain, record):
        response = self.api_call(
            'PUT',
            'domains/%s/records/%d' % (domain, record['id']),
            data=record
        )

        if 'domain_record' not in response:
            raise ApiError(response)

        return response


def update_ddns(domain, record_name, api_key):
    logging.info('starting dns update for %s/%s', domain, record_name)
    logging.debug('getting public ip')
    public_ip = get_public_ip()
    logging.debug('public ip detected as %s', public_ip,)
    api = DigitalOceanApi(api_key)
    record = api.get_record(domain, record_name)
    if record is None:
        logging.info('record does not exist, creating...')
        api.create_record(domain, record_name, public_ip)
        return

    if record['data'] != public_ip:
        logging.info('ips do not match, updating DNS')
        record['data'] = public_ip
        record['ttl'] = 60
        api.update_record(domain, record)
        return

    logging.info('already up to date')


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("api_key")
    parser.add_argument("domain")
    parser.add_argument("record")
    return parser.parse_args()


def main():
    args = parse_args()
    domain = args.domain
    record = args.record
    api_key = args.api_key
    update_ddns(domain, record, api_key)

if __name__ == "__main__":
    main()
