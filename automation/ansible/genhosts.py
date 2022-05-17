#!/usr/bin/env python3

# Copyright 2022 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from argparse import ArgumentParser
import logging
import subprocess
import sys


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())


def gen(prefix, domain, output, project=None):
    groups = {'all': [], 'stac': []}
    cmd = ['gcloud', 'compute', 'instances', 'list', '--format=value(NAME, EXTERNAL_IP)']
    if project:
        cmd += ['--project', project]
    # ansible inventory group
    # decode to utf8, split on newlines
    for line in subprocess.check_output(cmd).decode('utf8').split('\n'):
        logger.debug('raw line: %s', line)
        line = line.split()
        if len(line) != 2:
            continue
        if line[0].startswith(prefix):
            groups['stac'].append(line)
        else:
            groups['all'].append(line)

    def write_line(name, addr):
        try:
            output.write(f'{line[0]}.{domain}\n')
        except IndexError:
            logger.debug('skipping line %s', line)

    for line in groups['all']:
        write_line(*line)
    output.write('\n[stac]\n')
    for line in groups['stac']:
        write_line(*line)


def main():
    parser = ArgumentParser()
    parser.add_argument('prefix', nargs='?', default='node', help='node name prefix (default: node)')
    parser.add_argument('-o', '--output-file', default='hosts', help='output file (- for stdout)')
    parser.add_argument('-p', '--project', help='Google Cloud project to query')
    parser.add_argument('-d', '--domain', default='', help='Domain suffix to append to hostnames')
    parser.add_argument('-v', '--verbose', action='store_true')
    args = parser.parse_args()
    if args.verbose:
        logger.handlers[0].setLevel(logging.DEBUG)
    else:
        logger.handlers[0].setLevel(logging.WARNING)
    gen(args.prefix, args.domain, sys.stdout if args.output_file == '-' else open(args.output_file, 'w'))


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(1)
