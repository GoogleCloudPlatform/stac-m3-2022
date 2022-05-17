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

"""STAC-M3 data synchronization CLI."""

import argparse
from concurrent.futures import ThreadPoolExecutor, wait
import datetime
import logging
import os
from pathlib import Path
from re import match
import socket
import string
from subprocess import run, CompletedProcess, PIPE, STDOUT
import sys


logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stdout))


class TradingYear(list):
    """A list of days in a STAC-M3 trading year."""

    __holidays = [datetime.date(2011, 1, 17),
                  datetime.date(2011, 2, 21),
                  datetime.date(2011, 4, 22),
                  datetime.date(2011, 5, 30),
                  datetime.date(2011, 7, 4),
                  datetime.date(2011, 9, 5),
                  datetime.date(2011, 11, 24),
                  datetime.date(2011, 12, 26) ]

    def __init__(self, *args, year: int=__holidays[0].year, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.year = year
        base_year = self.__holidays[0].year

        day = datetime.date(base_year, 1, 1)
        while True:
            # exit once a new year is encountered
            if day.year != base_year:
                break
            if day not in self.__holidays and day.weekday() not in (5, 6):
                self.append(day)
            day += datetime.timedelta(days=1)

        # always generate base_year, then offset to the requested year
        if year != base_year:
            for idx, day in enumerate(self):
                self[idx] = day.replace(year=year)


class Shard(list):
    """A STAC-M3 kdb+ database shard."""

    def __init__(self, days: TradingYear, nodes: list, node_name: str, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.days = days
        self.nodes = nodes
        self.node_name = node_name

        for window_start in range(0, len(self.days), len(self.nodes)):
            window_end = window_start+len(self.nodes)
            window = self.days[window_start:window_end]
            logger.debug('start %s, end %s, window %s', window_start, window_end, window)
            try:
                self.append(window[self.nodes.index(node_name)])
            except IndexError:
                logger.debug('no day available for %s in window %s', node_name, window)


class LoopList(list):
    """A list that loops indefinitely from the last item to the first item."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__index = 0

    def __iter__(self):
        self.__index = 0
        return self

    def __next__(self):
        self.__index += 1
        return self[(self.__index-1) % len(self)]


def gsutil(src: str, dest: str) -> CompletedProcess:
    """Wrap gsutil with logging and output handling."""
    logger.info('copying %s to %s', src, dest)
    cmd = ('gsutil', '-m', 'cp', '-nr', src, dest)
    logger.debug('running %s', ' '.join(cmd))
    p = run(cmd, stdout=PIPE, stderr=STDOUT, check=True)
    logger.debug('%s -> %s:', src, dest)
    logger.debug(p.stdout.decode('utf8').strip())
    return p


def main() -> None:
    """Gather CLI arguments and run concurrent gsutil processes."""
    data_dir = Path('/m3/data')
    default_disks = []
    if data_dir.exists():
        for entry in data_dir.iterdir():
            if entry.is_dir() and match('^[0-9]+$', entry.name):
                default_disks.append(entry)
        default_disks.sort(key=lambda d: int(d.name.lstrip(string.ascii_letters)))
        default_disks = [str(d) for d in default_disks]

    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('nodes', nargs='+', help='nodes in cluster')
    parser.add_argument('-y', '--year', type=int, default=2011, help='year')
    parser.add_argument('-n', '--node', default=socket.gethostname(), help='local node name')
    parser.add_argument('-d', '--disks', nargs='+', default=default_disks, help='paths to data disk mounts')
    parser.add_argument('-u', '--storage-url', help='GCS storage path')
    parser.add_argument('-c', '--concurrency', default=len(default_disks), help='number of copies to run in parallel')
    parser.add_argument('-v', '--verbose', action='store_true', help='show debug info')
    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)
        logger.handlers[0].setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
        logger.handlers[0].setLevel(logging.INFO)

    if args.node not in args.nodes:
        logger.error('ERROR: node %r is not in the list of nodes: %s', args.node, ', '.join(args.nodes))
        sys.exit(1)

    shard = Shard(TradingYear(year=args.year), args.nodes, node_name=args.node)
    disks = LoopList(args.disks)
    futures = []
    with ThreadPoolExecutor(max_workers=args.concurrency) as executor:
        for day in shard:
            src = f'{args.storage_url.rstrip("/")}/{day.strftime("%Y.%m.%d")}'
            dest = next(disks)
            futures.append(executor.submit(gsutil, src, dest))
    # raise exceptions
    [f.result() for f in futures]
    os.sync()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(1)
