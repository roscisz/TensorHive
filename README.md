TODO Generate logo

TODO Generate svg badges with https://shields.io/#/examples/monitoring

# TensorHive
TODO Redesign description

## Advantages
## Demo
(See full gallery)[TODO link to screenshots of API docs and web app]

## Getting started
### Prerequisites
* cluster nodes should be accessible by SSH without password
* GPUs should support utilization monitoring through ```nvidia-smi```

### Installation
#### Via pip
```shell
pip install tensorhive
```
#### Via conda
```shell
conda install TODO
```
#### From source
```shell
git clone https://github.com/roscisz/TensorHive.git
cd TensorHive
pip install .
```
If you want to also build the web app:
```shell
(cd tensorhive/app/web/dev && npm install && npm run build)
```
### Usage
#### Required configuration
At first, you must tell TensorHive how it can establish SSH connections to hosts you want to work with.

You can do this by editing `~/.config/TensorHive/hosts_config.ini` [(see example)](https://github.com/roscisz/TensorHive/blob/feature/fixes_and_cleanups_before_release/tensorhive/hosts_config.ini)

#### Run TensorHive
```shell
tensorhive run
```

Dashboard: http://0.0.0.0:5000

Full API documentation (Swagger UI): http://0.0.0.0:1111/v0.2/ui

#### Optional configuration
You can fully customize TensorHive behaviour from `~/.config/TensorHive/config.ini`
[(see example)](https://github.com/roscisz/TensorHive/blob/feature/fixes_and_cleanups_before_release/tensorhive/default_config.ini)
  
### Features
#### Core
- [x] Monitor GPU parameters on each host
- [x] Protection of reserved resources
    - [x] Send warning messages to terminal of users who violate the rules
    - [ ] Send e-mail warnings
    - [ ] Kill unwated processes
- [ ] Automatic execution of user's predefined command
- [ ] Tracking wasted reservation time (idle)
    - [ ] Reservation start/end reminders
    - [ ] Send e-mail if idle for too long
#### Dashboard
- [x] Configurable charts view
    - [x] GPU metrics and active processes
    - [ ] CPU, RAM, HDD metrics
- [x] Calendar view
    - [x] Allow making reservations for selected GPUs
    - [x] Cancel reservations
- [ ] Detailed hardware specification view
- [ ] Admin panel
    - [ ] User banning
    - [ ] Accept/reject user's reservation

#### API
- [x] OpenAPI 2.0 specification with Swagger UI
- [ ] User authentication via JWT


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
