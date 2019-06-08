TensorHive
===

![](https://img.shields.io/badge/release-v0.3-brightgreen.svg?style=popout-square)
![](https://img.shields.io/badge/pypi-v0.3-brightgreen.svg?style=popout-square)
![](https://img.shields.io/badge/Issues%20and%20PRs-welcome-yellow.svg?style=popout-square)
![](https://img.shields.io/badge/platform-Linux-blue.svg?style=popout-square)
![](https://img.shields.io/badge/python-3.5%20|%203.6%20|%203.7-blue.svg?style=popout-square)
![](https://img.shields.io/badge/license-Apache%202.0-blue.svg?style=popout-square)

<img src="https://github.com/roscisz/TensorHive/raw/master/images/logo_small.png" height="130" align="left">

TensorHive is an open source system for monitoring and managing computing resources across multiple hosts.
It solves the most common problems and nightmares about accessing and sharing your AI-oriented infrastructure across multiple, often competing users.

It's designed with __simplicty, flexibility and configuration-friendliness__ in mind.

About project
----------------------
Our goal is to provide solutions for painful problems that ML engineers often have to struggle with when working with remote machines in order to run neural network trainings.

#### You should really consider using TensorHive if anything described in profiles below matches you:
1. You're an **admin**, who is responsible for managing a cluster (or multiple servers) with powerful GPUs installed.
- :angry: There are more users than resources, so they have to compete for it, but you don't know how to deal with that chaos
- :ocean: Other popular tools are simply an overkill, have different purpose or require a lot of time to spend on reading documentation, installation and configuration (Graphana, Kubernetes, Slurm)
- :penguin: People that are using your infrastructure expect only one interface for all the things related to training models (besides terminal): monitoring, reservation calendar and scheduling distributed jobs 
- :collision: Can't risk messing up sensitive configuration by installing software on each individual machine, prefering centralized solution which can be managed from one place.

2. You're a **standalone user** who has access to beefy GPUs scatterd across multiple machines.
- :part_alternation_mark: You want to be able to determine if batch size is too small or if there's a bottleneck when moving data from memory to GPU - charts with metrics such as `gpu_util`, `mem_util`, `mem_used` are great for this purpose
- :date: Visualizing names of training experiments using calendar helps you track how you're progressing on the project
- :snake: Launching distributed trainings is essential for you, no matter what the framework is
- :dizzy_face: Managing a list of training commands for all your distributed training experiments drives you nuts (because you didn't wrap them into bash scripts)
- :zzz: Remembering to manually launch the training before going sleep is no fun anymore

What TensorHive has to offer
-----------------------------
:zero: Dead-simple one-machine installation and configuration, no `sudo` requirements

:one: Users can make GPU reservations for specific time range in advance via **reservation mechanism**

&nbsp;&nbsp;&nbsp;&nbsp; :arrow_right: no more frustration caused by rules: **"first come, first served"** or **"the law of the jungle"**.

:two: Users can prepare and schedule custom tasks (commands) to be run on selected GPUs and hosts

&nbsp;&nbsp;&nbsp;&nbsp; :arrow_right: automate and simplify **distributed trainings** - **"one button to rule them all"**

:three: Gather all useful GPU metrics, from all configured hosts **in one dashboard**

&nbsp;&nbsp;&nbsp;&nbsp; :arrow_right: no more manually logging in to each individual machine in order to check if GPU is currently taken or not

For more details, check out the [full list of features](#features)

Getting started
---------------
### Prerequisites
* All hosts must be accessible via SSH, without password, using SSH Key-Based Authentication ([How to set up SSH keys](https://www.shellhacks.com/ssh-login-without-password/)
* Only NVIDIA GPUs are supported (relying on ```nvidia-smi``` command)

### Installation

#### via pip
```shell
pip install tensorhive
```

#### via conda
```shell
conda install tensorhive
```

#### From source
(optional) For development purposes we encourage separation from your current python packages using e.g. [Miniconda](https://docs.conda.io/en/latest/miniconda.html) 
`conda create --name th_env python=3.5 pip; activate th_env`

```shell
git clone https://github.com/roscisz/TensorHive.git && cd TensorHive
make dev
```
TensorHive is already shipped with newest web app build, but in case you modify the source, you can can build it with `make app`. For more useful commands see our [Makefile](https://github.com/roscisz/TensorHive/blob/master/tensorhive/Makefile).

Basic usage
-----
#### Run TensorHive
```shell
tensorhive
```

#### Required configuration
As you see, you must configure TensorHive so it knows how to establish SSH connections to hosts you want to work with.

You can do this by editing `~/.config/TensorHive/hosts_config.ini` after first `tensorhive` launch [(see example)](https://github.com/roscisz/TensorHive/blob/master/TensorHive/hosts_config.ini). In order to configure more hosts, just add a new section for each.


Web application and API Documentation can be accessed via URLs highlighted in green (Ctrl + click to open in browser)

#### Infrastructure monitoring dashboard

Accessible infrastructure can be monitored in the Nodes overview tab. Sample screenshot:

Here you can add new watches, configure displayed metrics, monitor running GPU processes and its' owners.


TODO Updated screenshot

#### GPU Reservation calendar

Each column represents all reservation events for a GPU on a given day.
In order to make a new reservation simply click and drag with your mouse, select GPU(s), add some meaningful title, optionally adjust time range.

If there are many hosts and GPUs in our infrastructure, you can use our simplified, horizontal calendar to quickly identify empty time slots and filter out already reserved GPUs.


TODO Updated screenshot

From now on, **only your processes are eligible to run on reserved GPU(s)**. TensorHive periodically checks if some other user has violated it. He will be spammed with warnings on all his PTYs, emailed every once in a while, additionally admin will also be notified (it all depends on the configuration).

#### Task nursery

Here you can prepare commands 
Simple but powerful command templating mechanism allows for **TODO**
Feel free to experiment **TODO**

Features
----------------------
#### Core
- [x] :mag_right: Monitor metrics on each host
    - [x] :tm: Nvidia GPUs
    - [ ] :pager: CPU, RAM, HDD
- [x] :customs: Protection of reserved resources
    - [x] :warning:	Send warning messages to terminal of users who violate the rules
    - [x] :mailbox_with_no_mail: Send e-mail warnings
    - [ ] :bomb: Kill unwanted processes
- [X] :rocket: Task nursery and scheduling
    - [x] :old_key: Execute any command in the name of a user
    - [x] :alarm_clock: Schedule spawn and termination
    - [x] :repeat: Synchronize process status
    - [x] :factory: Use `screen` command as backend - user can easily attach to running task
    - [x] :skull: Remote process interruption, termination and kill
    - [x] :floppy_disk: Save stdout to disk
    - [ ] :page_facing_up: Capture stderr
- [x] :watch: Track wasted (idle) time during reservation
    - [x] :hocho: Gather and calculate average gpu and mem utilization
    - [ ] :loudspeaker: Remind user when his reservation starts and ends
    - [ ] :incoming_envelope: Send e-mail if idle for too long
    
#### Web
- [x] :chart_with_downwards_trend: Configurable charts view
    - [x] Metrics and active processes
    - [ ] Detailed harware specification 
- [x] :calendar: Calendar view
    - [x] Allow making reservations for selected GPUs
    - [x] Edit reservations
    - [x] Cancel reservations
    - [ ] Attach jobs to reservation
- [x] :baby_symbol: Task nursery
    - [x] Create parametrized tasks and assign to hosts, automatically set `CUDA_VISIBLE_DEVICES`
    - [x] Buttons for task spawning/scheduling/termination/killing actions
    - [x] Fetch log produced by running task
    - [x] Group actions (spawn, schedule, terminate, kill selected)
- [ ] :straight_ruler: Detailed hardware specification panel (CPU clock speed, RAM, etc.)
- [ ] :penguin: Admin panel
    - [ ] User banning
    - [ ] Accept/reject reservation requests
    - [ ] Modify rules on-the-fly (without restarting)
    - [ ] Show popups to users (something like message of the day - `motd`)
    
#### CLI
- [ ] Implement command-line app that communicates with core via API
- [ ] Migrate all features from web app that don't require GUI (so no charts)

#### API
- [x] OpenAPI 2.0 specification with Swagger UI
- [x] User authentication via JWT

Deployment in production (for admins)
-----
#### Advanced configuration
You can fully customize TensorHive behaviour from `~/.config/TensorHive/main_config.ini`
[(see example)](https://github.com/roscisz/TensorHive/blob/master/tensorhive/main_config.ini)

#### Mailbot
TODO

#### Web
The last step is to launch TensorHive to the public so it can be accessed by users.
In order to do this you must open `~/.config/TensorHive/main_config.ini` and fill in `host` and `port` under `[web_app.server]` section (`host` field can be either a hostname or IP)


#### Database migrations
TODO


Currently TensorHive is being used on production in these 4 environments:

| Organization  | Hardware | No. users |
| ------ | -------- | --------- |
| ![](https://cdn.pg.edu.pl/ekontakt-updated-theme/images/favicon/favicon-16x16.png?v=jw6lLb8YQ4) [Gdansk University of Technology](https://eti.pg.edu.pl/en) | NVIDIA DGX Station (4x Tesla V100 16GB | TODO |
| ![](https://cdn.pg.edu.pl/ekontakt-updated-theme/images/favicon/favicon-16x16.png?v=jw6lLb8YQ4) [Lab at GUT](https://eti.pg.edu.pl/katedra-architektury-systemow-komputerowych/main) | 18x machines with GTX 1060 6GB | TODO |
| ![](http://martyniak.tech/images/gradient_logo_small-628ed211.png)[Gradient PG](http://gradient.eti.pg.gda.pl/en/) | TITAN X 12GB | TODO |
| ![](https://res-4.cloudinary.com/crunchbase-production/image/upload/c_lpad,h_20,w_20,f_auto,q_auto:eco/v1444894092/jeuh0l6opc159e1ltzky.png) [VoiceLab - Conversational Intelligence](voicelab.ai) | TODO | TODO

Application examples and benchmarks
--------
Along with TensorHive, we are developing a set of [**sample deep neural network training applications**](https://github.com/roscisz/TensorHive/tree/master/examples) in Distributed TensorFlow which will be used as test applications for the system. They can also serve as benchmarks for single GPU, distributed multi-GPU and distributed multi-node architectures. For each example, a full set of instructions to reproduce is provided.

<hr/>

Contibution and feedback
------------------------
We'd :heart: to collect your observations, issues and pull requests!

TODO Add issue template to repo. Put link to Issues here

You can do this by making use of our [**issue template**](https://gist.github.com/micmarty/396c649bf693688245731f35854bf971).

Credits
-------
Project created and maintained by:
- Paweł Rościszewski [(@roscisz)](https://github.com/roscisz)
- ![](https://avatars2.githubusercontent.com/u/12485656?s=22&v=4) [Michał Martyniak (@micmarty)](http://martyniak.me)
- Filip Schodowski [(@filschod)](https://github.com/filschod)

 Top contributions:
- Tomasz Menet [(@tomenet)](https://github.com/tomenet)
- Dariusz Piotrowski [(@PiotrowskiD)](https://github.com/PiotrowskiD)
- Karol Draszawka [(@szarakawka)](https://github.com/szarakawka)


License
-------
[Apache License 2.0](https://github.com/roscisz/TensorHive/blob/master/LICENSE)
