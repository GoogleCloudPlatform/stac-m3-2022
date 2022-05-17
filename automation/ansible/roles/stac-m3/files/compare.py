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
import csv
import logging
import sys


# antuco google MBps
#1T.YRHIBID.MBPS 6,792 7,006
#1T.YRHIBID-2.MBPS 9,098 10,981
#1T.QTRHIBID.MBPS 5,725 6,186
#1T.MOHIBID.MBPS 1,992 2,201
#1T.WKHIBID.MBPS 567 593

COL_WIDTH = 20
COLORS = 'auto'

baselines = {
    '2018': {
        '1T.WKHIBID.TIME': [152, 158],
        '1T.MOHIBID.TIME': [177, 194],
        '1T.QTRHIBID.TIME': [180, 188],
        '1T.YRHIBID.TIME': [653, 682],
        '1T.YRHIBID-2.TIME': [461, 537],
        '1T.VWAB-D.TIME': [120, 136],
        '10T.THEOPL.TIME': [321, 332, 149, 524, 103],
        '10T.MKTSNAP.TIME': [1735, 1683, 1553, 2043, 147],
        '10T.VOLCURV.TIME': [7409, 7381, 1346, 13839, 3794],
        '10T.STATS-AGG.TIME': [6858, 6752, 1191, 12828, 3608],
        '1T.STATS-UI.TIME': [460, 437, 409, 542, 52],
        '10T.STATS-UI.TIME': [1411, 1369, 157, 2822, 778],
        '50T.STATS-UI.TIME': [6214, 6333, 171, 12066, 3356],
        '100T.STATS-UI.TIME': [10351, 9951, 626, 22439, 6366],
        '100T.VWAB-12D-NO.TIME': [9549, 9223, 782, 19093, 4306],
        '1T.WRITE.TIME': [14091, 16001],
        '1T.NBBO.TIME': [29005, 29740]
    }
}


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())


def get_diff(baseline, value):
    """Calculate the difference between two values as an integer value and a
    percentage and return a string formatted for display.
    """
    if COLORS == 'always' or (COLORS == 'auto' and sys.stdout.isatty()):
        normal = '\033[0m'
        red    = '\033[31m'
        green  = '\033[32m'
        yellow = '\033[33m'
        # adjust for ANSI control codes, assuming two color-formatted tokens
        unprintable_length = 18
    else:
        normal = ''
        red    = ''
        green  = ''
        yellow = ''
        unprintable_length = 0

    baseline = int(round(baseline, 0))
    value = int(round(value, 0))
    diff = value - baseline
    pct_diff = int(round((diff / baseline) * 100, 0))

    if diff <= 0:
        output = f'{value} {green}{diff}{normal}/{green}{pct_diff}%{normal}'
    else:
        if pct_diff >= 25:
            color = red
        else:
            color = yellow
        output = f'{value} {color}+{diff}{normal}/{color}+{pct_diff}%{normal}'

    return output.center(COL_WIDTH + unprintable_length)


def print_separator():
    """Print a table separator line.
    """
    for _ in range(6):
        sys.stdout.write('+'.ljust(COL_WIDTH + 1, '-'))
    sys.stdout.write('+\n')


def compare(baseline, benchmarks_path):
    if not benchmarks_path.endswith('benchmarks.csv'):
        benchmarks_path = f'{benchmarks_path.rstrip("/")}/benchmarks.csv'
    with open(benchmarks_path) as benchmarks:
        print_separator()
        # table header
        sys.stdout.write('|')
        for header in ('Test', 'Mean', 'Median', 'Min', 'Max', 'Std Dev'):
            sys.stdout.write(f' {header.center(18)} |')
        sys.stdout.write('\n')
        print_separator()

        # skip header row
        for row in benchmarks.readlines()[1:]:
            row = row.split(',')
            rootid = row[0]
            mean, median, min, max, stdv, _ = [float(item) for item in row[1:]]
            baseline_stats = baselines[baseline].get(rootid, None)
            if not baseline_stats:
                logger.warning('no baseline stats found for %s', rootid)
            else:
                sys.stdout.write('|')
                sys.stdout.write(f'{rootid[0:-5].center(COL_WIDTH)}|')
                sys.stdout.write(f'{get_diff(baseline_stats[0], mean)}|')
                if len(baseline_stats) == 2:
                    sys.stdout.write(f'{"".ljust(COL_WIDTH)}|')
                    sys.stdout.write(f'{"".ljust(COL_WIDTH)}|')
                    sys.stdout.write(f'{get_diff(baseline_stats[1], max)}|')
                    sys.stdout.write(f'{"".ljust(COL_WIDTH)}|\n')
                else:
                    sys.stdout.write(f'{get_diff(baseline_stats[1], median)}|')
                    sys.stdout.write(f'{get_diff(baseline_stats[2], min)}|')
                    sys.stdout.write(f'{get_diff(baseline_stats[3], max)}|')
                    sys.stdout.write(f'{get_diff(baseline_stats[4], stdv)}|\n')
                print_separator()


def main():
    parser = ArgumentParser()
    parser.add_argument('-b', '--benchmarks', default='benchmarks.csv',
                        help='path to benchmarks.csv from a test run')
    parser.add_argument('-B', '--baseline', choices=baselines.keys(),
                        default='2018', help='baseline dataset for comparison')
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('-w', '--column-width', type=int)
    parser.add_argument('-c', '--colors', choices=('auto', 'never', 'always'), default='auto')
    args = parser.parse_args()
    if args.verbose:
        logger.handlers[0].setLevel(logging.DEBUG)
    else:
        logger.handlers[0].setLevel(logging.WARNING)
    global COLORS
    COLORS = args.colors
    compare(args.baseline, args.benchmarks)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(1)
