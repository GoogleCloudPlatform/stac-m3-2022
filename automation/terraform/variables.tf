/**
 * Copyright 2022 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

variable project {}

variable region {
  default = "us-east1"
}

variable zone {
  default = "us-east1-b"
}

variable instance_count {
  default = 12
}

variable name {
  default = "node"
}

variable machine_type {
  default = "n2-custom-32-163840"
}

variable cpu_platform {
  default = "Intel Cascade Lake"
}

variable boot_disk_type {
  default = "pd-ssd"
}

variable boot_disk_size {
  default = 4096
}

variable boot_disk_image {
  default = "ubuntu-os-cloud/ubuntu-2004-lts"
}

variable scopes {
  default = ["storage-ro", "logging-write"]
}

variable data_disk_mode {
  default = "READ_ONLY"
}

variable dns_zone {
  type = string
}

variable dns_domain {
  type = string
}
