#!/bin/bash

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

pushd "$(dirname $0)"

ANTUCO_ID="antuco-sharded-gcp-$(date +%Y%m%d)"
KANAGA_ID="kanaga-sharded-gcp-$(date +%Y%m%d)"

script $ANTUCO_ID.log -c "./runm3-antuco.sh $ANTUCO_ID" <<< y
gzip -f $ANTUCO_ID.log

script $KANAGA_ID.log -c "./runm3-kanaga.sh $KANAGA_ID" <<< y
gzip -f $KANAGA_ID.log

popd
