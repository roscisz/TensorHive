<img src="https://github.com/roscisz/TensorHive/raw/master/images/logo_small.png" height="200">

TensorHive
===


![](https://img.shields.io/badge/release-v0.2.3-brightgreen.svg?style=popout-square)
![](https://img.shields.io/badge/pypi-v0.2.3-brightgreen.svg?style=popout-square)
![](https://img.shields.io/badge/platform-Linux-blue.svg?style=popout-square)
![](https://img.shields.io/badge/python-3.5%20|%203.6%20|%203.7-blue.svg?style=popout-square)
![](https://img.shields.io/badge/license-Apache%202.0-blue.svg?style=popout-square)

TensorHive is an open source system for managing and monitoring your computing resources across multiple hosts.
It solves the most common problems and nightmares about accessing and sharing your AI-focused infrastructure across multiple, often competing users.

It's designed with __flexibility, lightness and configuration-friendliness__ in mind. 

Getting started
---------------
### Prerequisites
* Nodes should be accessible via SSH without password ([HOWTO set up SSH keys](https://www.ssh.com/ssh/keygen/))
* Only NVIDIA GPUs are supported (```nvidia-smi``` is required)

### Installation

#### Via pip
```shell
pip3 install tensorhive
```

#### From source
```
git clone https://github.com/roscisz/TensorHive.git
cd TensorHive
pip install .
```

If you want to also build the web app manually:
```shell
(cd tensorhive/app/web/dev && npm install && npm run build)
```

Usage
-----
#### Required configuration
At first, you must tell TensorHive how it can establish SSH connections to hosts you want to work with.

You can do this by editing `~/.config/TensorHive/hosts_config.ini` [(see example)](https://github.com/roscisz/TensorHive/blob/master/hosts_config.ini)

#### Run TensorHive
```shell
tensorhive
```
Sample output:
<img src="https://raw.githubusercontent.com/roscisz/TensorHive/master/images/console_screenshot.png">

The Web application and API Documentation can be accessed through te given URLs.

If you need the Web application to be accessible from remote machines, set the `host` and `port` fields in the
`[web_app.server]` section in `~/.config/TensorHive/main_config.ini`. The host field should be set to a hostname
or IP that resolves to an external network interface.

#### Monitor infrastructure

The available infrastructure can be monitored in the Nodes overview tab. Sample screenshot:

<img src="https://raw.githubusercontent.com/roscisz/TensorHive/master/images/nodes_overview_screenshot.png" height="600">

The "Add watch" button allows to add a new chart which can be configured to show chosen metrics of the selected devices. Currently, the metrics include GPU metrics from nvidia-smi and a process overview with corresponding usernames.

#### Reserve resources

The computing resource reservations can be viewed and managed in the Reservations overview tab. Sample screenshot:

<img src="https://raw.githubusercontent.com/roscisz/TensorHive/master/images/reservations_overview_screenshot.png" height="600">

The select boxes at the bottom of the page (easily accessible by the Adjust Filters button) allow to specify which nodes or devices should be visible in the view. Adding reservations is possible through selecting a time interval and filling the reservation details in a form. Cancelling reservations is possible for the reservation owner and admin user by clicking on a given reservation and confirming the cancellation.

#### Optional configuration
You can fully customize TensorHive behaviour from `~/.config/TensorHive/main_config.ini`
[(see example)](https://github.com/roscisz/TensorHive/blob/master/main_config.ini)


Features
--------
#### Core
- [x] :mag_right: Monitor GPU parameters on each host
- [x] :customs: Protection of reserved resources
    - [x] :warning:	Send warning messages to terminal of users who violate the rules
    - [x] :mailbox_with_no_mail: Send e-mail warnings
    - [ ] :bomb: Kill unwated processes
- [ ] :rocket: Automatic execution of user's predefined command
- [x] :watch: Track wasted reservation time (idle)
    - [ ] Remind user when his reservation starts and ends
    - [ ] Send e-mail if idle for too long
#### Dashboard
- [x] :chart_with_downwards_trend: Configurable charts view
    - [x] GPU metrics and active processes
    - [ ] CPU, RAM, HDD metrics
- [x] :calendar: Calendar view
    - [x] Allow making reservations for selected GPUs
    - [x] Edit reservations
    - [x] Cancel reservations
- [ ] :scroll: Detailed hardware specification view
- [ ] :penguin: Admin panel
    - [ ] User banning
    - [ ] Accept/reject reservation requests

#### API
- [x] OpenAPI 2.0 specification with Swagger UI
- [x] User authentication via JWT


Application examples and benchmarks
--------
Along with TensorHive, we are developing a set of [**sample deep neural network training applications**](https://github.com/roscisz/TensorHive/tree/master/examples) in Distributed TensorFlow which will be used as test applications for the system. They can also serve as benchmarks for various GPU, distributed multiGPU and distributed multinode architectures. For each example, a full set of instructions to reproduce is given.

<hr/>

Contibution and feedback
------------------------
We'd :heart: to collect your observations, issues and pull requests.

You can do this by making use of our [**issue template**](https://gist.github.com/micmarty/396c649bf693688245731f35854bf971).

Credits
-------
Project created and maintained by:
- Paweł Rościszewski [(@roscisz)](https://github.com/roscisz)
- ![](https://avatars2.githubusercontent.com/u/12485656?s=22&v=4) [Michał Martyniak (@micmarty)](http://martyniak.me)
- Filip Schodowski [(@filschod)](https://github.com/filschod)
- Tomasz Menet [(@tomenet)](https://github.com/tomenet)
- Karol Draszawka [(@szarakawka)](https://github.com/szarakawka)

License
-------
[Apache License 2.0](https://github.com/roscisz/TensorHive/blob/master/LICENSE)
