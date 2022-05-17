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

provider google {
  project = var.project
}

resource google_compute_instance node {
  count = var.instance_count
  name = "${var.name}${format("%02s", count.index + 1)}"
  machine_type = var.machine_type
  zone = var.zone
  allow_stopping_for_update = true
  min_cpu_platform = var.cpu_platform

  scheduling {
    on_host_maintenance = "MIGRATE"
    automatic_restart = false
  }

  service_account {
      scopes = var.scopes
  }

  boot_disk {
    initialize_params {
      image = var.boot_disk_image
      size = var.boot_disk_size
      type = var.boot_disk_type
    }
  }

  # 8
  scratch_disk { interface = "NVME" }
  scratch_disk { interface = "NVME" }
  scratch_disk { interface = "NVME" }
  scratch_disk { interface = "NVME" }
  scratch_disk { interface = "NVME" }
  scratch_disk { interface = "NVME" }
  scratch_disk { interface = "NVME" }
  scratch_disk { interface = "NVME" }

  # 16
  # only valid for N2 machine types
  scratch_disk { interface = "NVME" }
  scratch_disk { interface = "NVME" }
  scratch_disk { interface = "NVME" }
  scratch_disk { interface = "NVME" }
  scratch_disk { interface = "NVME" }
  scratch_disk { interface = "NVME" }
  scratch_disk { interface = "NVME" }
  scratch_disk { interface = "NVME" }

  # 24
  # only valid for N2 machine types
  scratch_disk { interface = "NVME" }
  scratch_disk { interface = "NVME" }
  scratch_disk { interface = "NVME" }
  scratch_disk { interface = "NVME" }
  scratch_disk { interface = "NVME" }
  scratch_disk { interface = "NVME" }
  scratch_disk { interface = "NVME" }
  scratch_disk { interface = "NVME" }

  network_interface {
    network = "default"
    nic_type = "GVNIC"
    access_config {
      network_tier = "PREMIUM"
    }
  }
}

resource google_dns_record_set node {
  count = var.instance_count
  managed_zone = var.dns_zone
  name = "${var.name}${format("%02s", count.index + 1)}.${var.dns_domain}."
  type = "A"
  rrdatas = ["${google_compute_instance.node[count.index].network_interface[0].access_config[0].nat_ip}"]
  ttl = 5
}

resource google_compute_instance runner {
  name = "runner"
  machine_type = var.machine_type
  zone = var.zone
  allow_stopping_for_update = true

  scheduling {
    on_host_maintenance = "MIGRATE"
    automatic_restart = false
  }

  service_account {
      scopes = var.scopes
  }

  boot_disk {
    initialize_params {
      image = var.boot_disk_image
      size = var.boot_disk_size
      type = var.boot_disk_type
    }
  }

  network_interface {
    network = "default"
    nic_type = "GVNIC"
    access_config {
      network_tier = "PREMIUM"
    }
  }
}

resource google_dns_record_set runner {
  managed_zone = var.dns_zone
  name = "runner.${var.dns_domain}."
  type = "A"
  rrdatas = ["${google_compute_instance.runner.network_interface[0].access_config[0].nat_ip}"]
  ttl = 5
}
