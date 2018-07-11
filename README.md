# TensorHive

## About
TensorHive is a work in progress project with the objective to develop a **lightweight computing resource management tool for executing machine learning applications in distributed [TensorFlow](https://github.com/tensorflow/tensorflow).**

Core feature of TensorHive is to allow for easy execution of distributed trainings without the need for manual logging into every worker node or installing and configuring resource management daemons.

Further plans include: 
* task and hardware queuing
* support for machine learning applications in frameworks other than TensorFlow

## Roadmap:
(Due to funding delays, the milestones have been modified)

### Resource reservation module
  * Beta: **31.07.2018**
  * Final release: **31.12.2018**
  
### Executing distributed TensorFlow applications
  * Beta: **30.09.2018**
  
## Current features
- [x] Connect to multiple nodes via SSH
- [x] Monitor basic GPU parameters on every host
- [x] Define very basic OpenAPI specification
- [x] Command Line interface
- [ ] Users can make reservations using calendar
- [ ] Priviliged users can view resource utilization on charts (CPU, GPU, mem, disk)
- [ ] During the reservation period users can freely access declared resources
- [ ] When reservation time expires (or before it starts), user processes are stopped
- [ ] Admin dashboard (ban users, edit/reject reservations)

## Demo

[![asciicast](https://asciinema.org/a/hzQMCvvZMqtv8mtCafQ0l4TFk.png)](https://asciinema.org/a/hzQMCvvZMqtv8mtCafQ0l4TFk)

<table>
<thead>
<tr>
<th>tensorhive run core</th>
<th>tensorhive run api</th>
</tr>
</thead>
<tbody>
<tr>
<td><img src="https://i.imgur.com/lkTv5xH.png" alt="tensorhive run core - screenshot"></td>
<td><img src="https://i.imgur.com/sR4PAbZ.png" alt="tensorhive run api - screenshot"></td>
</tr>
</tbody>
</table>

## Requirements

* cluster nodes should be accessible by SSH without password
* GPUs should support utilization monitoring through ```nvidia-smi```

## Installation
```shell
git clone https://github.com/roscisz/TensorHive.git
cd TensorHive
pip install .
```

## Usage
1. Run TensorHive core:
```shell
# You need to modify info about your ssh-available hosts in SSHConfig (tensorhive/config.py)
tensorhive run core
```
2. Run TensorHive API server
```shell
tensorhive db init
tensorhive run api
```
Explore full API documentation with examples at http://0.0.0.0:9876/v1.0/ui/#/default 
