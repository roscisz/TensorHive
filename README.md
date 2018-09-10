<img src="https://i.imgur.com/7GtwA5G.png" width="400">

TensorHive
===


![](https://img.shields.io/badge/release-v0.2-brightgreen.svg?style=popout-square)
![](https://img.shields.io/badge/pypi-v0.2-brightgreen.svg?style=popout-square)
![](https://img.shields.io/badge/platform-Linux-blue.svg?style=popout-square)
![](https://img.shields.io/badge/python-3.5%20|%203.6%20|%203.7-blue.svg?style=popout-square)
![](https://img.shields.io/badge/license-Apache%202.0-blue.svg?style=popout-square)

TensorHive is an open source system for managing and monitoring your computing resources across multiple hosts.
It solves the most common problems and nightmares about accessing and sharing your AI-focused infrastructure across multiple, often competing users.

It's designed with __flexibility, lightness and configuration-friendliness__ in mind. 

Test bed and benchmarks
--------
[**NVIDIA DGX STATION (4x NVIDIA Tesla® V100 32GB)**](https://www.nvidia.com/content/dam/en-zz/Solutions/Data-Center/dgx-station/dgx-station-print-dgx-station-32GB-infographic-final-LR.pdf) and a bunch of nodes with GTX 1060 on board.

You can check out our **unique** benchamark results with a full set instructions to reproduce (both in Distributed TensorFlow):
- [**DeepSpeech README**](https://github.com/roscisz/TensorHive/tree/develop/examples/deepspeech#deepspeech-benchmarks)
- [**T2T Transformer README**](https://github.com/roscisz/TensorHive/tree/develop/examples/t2t_transformer#t2t-transformer-benchmarks)
<hr/>

TODO
- Maybe expand description
- Put GIF here
- (See full gallery)[TODO link to screenshots of API docs and web app]

Getting started
---------------
### Prerequisites
* Nodes should be accessible via SSH without password (how to)[TODO tutorial link, generating keys]
* Only NVIDIA GPUs are supported (```nvidia-smi``` is required)

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

You can do this by editing `~/.config/TensorHive/hosts_config.ini` [(see example)](https://github.com/roscisz/TensorHive/blob/feature/fixes_and_cleanups_before_release/tensorhive/hosts_config.ini)

#### Run TensorHive
```shell
tensorhive run
```
Open **Dashboard** http://0.0.0.0:5000

Open **API docs** http://0.0.0.0:1111/api/0.2/ui

#### Optional configuration
You can fully customize TensorHive behaviour from `~/.config/TensorHive/config.ini`
[(see example)](https://github.com/roscisz/TensorHive/blob/feature/fixes_and_cleanups_before_release/tensorhive/default_config.ini)
  
Features
--------
#### Core
- [x] :mag_right: Monitor GPU parameters on each host
- [x] :customs: Protection of reserved resources
    - [x] :warning:	Send warning messages to terminal of users who violate the rules
    - [ ] :mailbox_with_no_mail: Send e-mail warnings
    - [ ] :bomb: Kill unwated processes
- [ ] :rocket: Automatic execution of user's predefined command
- [ ] :watch: Track wasted reservation time (idle)
    - [ ] Remind user when his reservation starts and ends
    - [ ] Send e-mail if idle for too long
#### Dashboard
- [x] :chart_with_downwards_trend: Configurable charts view
    - [x] GPU metrics and active processes
    - [ ] CPU, RAM, HDD metrics
- [x] :calendar: Calendar view
    - [x] Allow making reservations for selected GPUs
    - [x] Cancel reservations
- [ ] :scroll: Detailed hardware specification view
- [ ] :penguin: Admin panel
    - [ ] User banning
    - [ ] Accept/reject reservation requests

#### API
- [x] OpenAPI 2.0 specification with Swagger UI
- [ ] User authentication via JWT


Contibution and feedback
------------------------
We'd :heart: to collect your observations, issues and pull requests.

You can do this by making use of our [**issue template**](https://gist.github.com/micmarty/396c649bf693688245731f35854bf971).

Credits
-------
Project created and maintained by:
- Paweł Rościszewski
- ![](https://avatars2.githubusercontent.com/u/12485656?s=22&v=4) [Michał Martyniak](http://martyniak.me)
- Filip Schodowski
- Tomasz Menet

License
-------
[Apache License 2.0](https://github.com/roscisz/TensorHive/blob/master/LICENSE)
