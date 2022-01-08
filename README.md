TensorHive
===
![](https://img.shields.io/badge/release-v1.0.0-brightgreen.svg?style=popout-square)
![](https://img.shields.io/badge/pypi-v1.0.0-brightgreen.svg?style=popout-square)
![](https://img.shields.io/badge/Issues%20and%20PRs-welcome-yellow.svg?style=popout-square)
![](https://img.shields.io/badge/platform-Linux-blue.svg?style=popout-square)
![](https://img.shields.io/badge/hardware-Nvidia-green.svg?style=popout-square)
![](https://img.shields.io/badge/python-3.5%20|%203.6%20|%203.7%20|%203.8-blue.svg?style=popout-square)
![](https://img.shields.io/badge/license-Apache%202.0-blue.svg?style=popout-square)

<img src="https://github.com/roscisz/TensorHive/raw/master/images/logo_small.png" height="130" align="left">

TensorHive is an open source tool for managing computing resources used by multiple users across distributed hosts. It focuses on granting exclusive access to GPUs for machine learning workloads and consists of __reservation__, __monitoring__ and __job execution__ modules.

It's designed with __simplicity, flexibility and configuration-friendliness__ in mind.

---------------

### Main features:

#### GPU Reservation calendar

Each column represents all reservation events for a GPU on a given day.
In order to make a new reservation simply click and drag with your mouse, select GPU(s), add some meaningful title, optionally adjust time range.
If there are many hosts and GPUs in our infrastructure, you can use our simplified, horizontal calendar to quickly identify empty time slots and filter out already reserved GPUs.
![image](https://raw.githubusercontent.com/roscisz/TensorHive/master/images/reservations_overview_screenshot.png)

From now on, **only your processes are eligible to run on the reserved GPU(s)**. TensorHive periodically checks if some other user has violated it. They will be spammed with warnings on all his PTYs, emailed every once in a while, additionally admin will also be notified (it all depends on the configuration).

Terminal warning             |  Email warning             |  Admin warning
:-------------------------:|:-------------------------:|:-------------------------:
![image](https://raw.githubusercontent.com/roscisz/TensorHive/master/images/terminal_warning_screenshot.png)  |  ![image](https://raw.githubusercontent.com/roscisz/TensorHive/master/images/email_warning_screenshot.png) | ![image](https://raw.githubusercontent.com/roscisz/TensorHive/master/images/admin_warning_screenshot.png)
 


#### Infrastructure monitoring dashboard
Accessible infrastructure can be monitored in the Nodes overview tab. Sample screenshot:
Here you can add new watches, select metrics and monitor ongoing GPU processes and their owners.

![image](https://raw.githubusercontent.com/roscisz/TensorHive/master/images/nodes_overview_screenshot.png)

#### Job execution

Thanks to the `Job execution` module, you can define commands for tasks you want to run on any configured nodes.
You can manage them manually, set specific spawn/terminate dates or add jobs to a queue, so that they are executed automatically
when the required resources are not reserved.
Commands are run within `screen` session, so attaching to it while they are running is a piece of cake.

It provides a simple, but flexible (**framework-agnostic**) command templating mechanism that will help you automate multi-node trainings.
Additionally, specialized templates help to conveniently set proper parameters for chosen well known frameworks. In the [examples](https://github.com/roscisz/TensorHive/tree/master/examples) directory, you will find sample scenarios of using the `Job execution` module for various
frameworks (including TensorFlow and PyTorch) and computing environments.

![image](https://raw.githubusercontent.com/roscisz/TensorHive/master/examples/TF_CONFIG/img/multi_process.png)

TensorHive requires that users who want to use this feature must append TensorHive's public key to their `~/.ssh/authorized_keys` on all nodes they want to connect to.

---------------

### Use cases

Our goal is to provide solutions for painful problems that ML engineers often have to struggle with when working with remote machines in order to run neural network trainings.

#### You should really consider using TensorHive if anything described in profiles below matches you:
1. You're an **admin**, who is responsible for managing a cluster (or multiple servers) with powerful GPUs installed.
- :angry: There are more users than resources, so they have to compete for it
- :microphone: The users require __exclusive access__ to the GPUs, rather than a queuing system 
- :crystal_ball: You need to control which projects in your organization consume the most computing power
- :ocean: Other popular tools are simply an overkill, have different purpose or require a lot of time to spend on reading documentation, installation and configuration (Grafana, Kubernetes, Slurm)
- :penguin: People using your infrastructure expect only one interface for all the things related to managing computing infrastructure: monitoring, reservation calendar and scheduling distributed jobs
- :collision: Can't risk messing up sensitive configuration by installing software on each individual machine, prefering centralized solution which can be managed from one place

2. You're a **standalone user** who has access to beefy GPUs scattered across multiple machines.
- :part_alternation_mark: You want to keep the GPU utilization high, considering batch size, host to device data transfer etc. - charts with metrics such as `gpu_util`, `mem_util`, `mem_used` are great for this purpose
- :date: Visualizing names of training experiments using calendar helps you track how you're progressing on the project
- :snake: Launching distributed trainings is essential for you, no matter what the framework is
- :dizzy_face: Managing a list of training commands for all your distributed training experiments drives you nuts
- :zzz: Remembering to manually launch the training before going sleep is no fun anymore

#### Advantages of TensorHive 

:zero: Dead-simple one-machine installation and configuration, no `sudo` requirements

:one: Users can make GPU reservations for specific time range in advance via **reservation mechanism**

&nbsp;&nbsp;&nbsp;&nbsp; :arrow_right: no more frustration caused by rules: **"first come, first served"** or **"the law of the jungle"**.

:two: Users can prepare and schedule custom tasks (commands) to be run on selected GPUs and hosts

&nbsp;&nbsp;&nbsp;&nbsp; :arrow_right: automate and simplify **distributed trainings** - **"one button to rule them all"**

:three: Gather all useful GPU metrics, from all configured hosts **in one dashboard**

&nbsp;&nbsp;&nbsp;&nbsp; :arrow_right: no more manual logging in to each individual machine in order to check if GPU is currently in use or not

:four: Access to specific GPUs or hosts can be granted to specific users or groups

&nbsp;&nbsp;&nbsp;&nbsp; :arrow_right: division of the infrastructure can be easily adjusted to the current needs of work groups in your organization

:five: Automatic execution of queued jobs when there are no active GPU reservations

&nbsp;&nbsp;&nbsp;&nbsp; :arrow_right: jobs that are not urgent can be added to a queue and automatically executed later


---------------

### Getting started

#### Prerequisites
* All nodes must be accessible via SSH, without password, using SSH Key-Based Authentication ([How to set up SSH keys](https://www.shellhacks.com/ssh-login-without-password/) - explained in [Quickstart section](#basic-usage))
* Only NVIDIA GPUs are supported (relying on ```nvidia-smi``` command)
* Currently TensorHive assumes that all users who want to register into the system must have identical UNIX usernames on all nodes configured by TensorHive administrator (not relevant for standalone developers)
* (optional) We recommend installing TensorHive on a separate user account (for example `tensorhive`) and adding this user to the `tty` system group.

#### Installation

##### via pip
```shell
pip install tensorhive
```

##### From source
(optional) For development purposes we encourage separation from your current python packages using e.g. virtualenv, Anaconda. 

```shell
git clone https://github.com/roscisz/TensorHive.git && cd TensorHive
pip install -e .
```

TensorHive is already shipped with newest web app build, but in case you modify the source, you can can build it with `make app`. For more useful commands see our [Makefile](https://github.com/roscisz/TensorHive/blob/master/tensorhive/Makefile).
Build tested with `Node v14.15.4` and `npm 6.14.10`

#### Basic usage

###### Quickstart
The `init` command will guide you through basic configuration process:
```
tensorhive init
```

You can check connectivity with the configured hosts using the `test` command.
```
tensorhive test
```

(optional) If you want to allow your UNIX users to set up their TensorHive accounts on their own and run distributed
programs through `Job execution` module, use the `key` command to generate the SSH key for TensorHive: 
```
tensorhive key
```

Now you should be ready to launch a TensorHive instance:
```
tensorhive
```

Web application and API Documentation can be accessed via URLs highlighted in green (Ctrl + click to open in browser).

##### Advanced configuration
You can fully customize TensorHive behaviours via INI configuration files (which will be created automatically after `tensorhive init`):
```
~/.config/TensorHive/hosts_config.ini
~/.config/TensorHive/main_config.ini
~/.config/TensorHive/mailbot_config.ini
```
<details>
<summary>(see example)</summary>
<p>

[hosts_config.ini](https://github.com/roscisz/TensorHive/blob/master/tensorhive/hosts_config.ini)
[main_config.ini](https://github.com/roscisz/TensorHive/blob/master/tensorhive/main_config.ini)
[mailbot_config.ini](https://github.com/roscisz/TensorHive/blob/master/tensorhive/mailbot_config.ini)


</p>
</details>

----------------------

#### Reverse proxy setup

Serving TensorHive through reverse proxy requires proper configuration of URL parameters in the `[api]` section of
`main_config.ini`, including `url_schema`, `url_hostname`, `url_port` and `url_prefix`.

<details>
<summary>(see example)</summary>
<p>

Let's assume that the WebApp is served locally on `http://localhost:5000`, the API on `http://localhost:1111` and we
want to serve TensorHive publicly at `https://some-server/tensorhive`. In such case the following `main_config.ini`:

```
url_schema = https
url_hostname = some-server
url_port = 443
url_prefix = tensorhive/api
```
should be used along with a reverse proxy similar to the following example for nginx:

```
location /tensorhive {
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-Host $host:$server_port;
    proxy_set_header X-Forwarded-Server $host;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

    add_header 'Access-Control-Allow-Origin' '*';
    add_header 'Access-Control-Allow-Credentials' 'true';
    add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS';
    add_header 'Access-Control-Allow-Headers' 'DNT,X-CustomHeader,Keep-Alive,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type';

    proxy_pass  http://localhost:5000/tensorhive;
    proxy_set_header SCRIPT_NAME /tensorhive;
}

location /tensorhive/api {
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-Host $host:$server_port;
    proxy_set_header X-Forwarded-Server $host;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

    add_header 'Access-Control-Allow-Origin' '*';
    add_header 'Access-Control-Allow-Credentials' 'true';
    add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS';
    add_header 'Access-Control-Allow-Headers' 'DNT,X-CustomHeader,Keep-Alive,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type';

    proxy_pass  http://localhost:1111;
}
```

</p>
</details>

Contribution and feedback
------------------------
We'd :heart: to collect your observations, issues and pull requests!

Feel free to **report any configuration problems, we will help you**.

Currently we are gathering practical infrastructure protection scenarios from our users to extract and further support the most common TensorHive deployments.

If you consider becoming a contributor, please look at issues labeled as 
[**good-first-issue**](https://github.com/roscisz/TensorHive/issues?q=is%3Aissue+is%3Aopen+label%3Agood-first-issue)
and
[**help wanted**](https://github.com/roscisz/TensorHive/issues?q=is%3Aissue+is%3Aopen+label%3A%22help+wanted%22).

Credits
-------

Project created and maintained by:
- Paweł Rościszewski [(@roscisz)](https://github.com/roscisz)
- ![](https://avatars2.githubusercontent.com/u/12485656?s=22&v=4) [Michał Martyniak (@micmarty)](https://micmarty.github.io)
- Filip Schodowski [(@filschod)](https://github.com/filschod)

 Top contributors:
- Jacek Szempliński [(@jszemplinski)](https://github.com/jszemplinski)
- Mateusz Piotrowski [(@matpiotrowski)](https://github.com/matpiotrowski)
- Martyna Oleszkiewicz [(@martyole)](https://github.com/martyole)
- Tomasz Menet [(@tomenet)](https://github.com/tomenet)
- Bartosz Jankowski [(@brtjank)](https://github.com/brtjank)

TensorHive has been greatly supported within a joint project between [**VoiceLab.ai**](https://voicelab.ai) and
[**Gdańsk University of Technology**](https://pg.edu.pl/) titled: "Exploration and selection of methods
for parallelization of neural network training using multiple GPUs".


License
-------
[Apache License 2.0](https://github.com/roscisz/TensorHive/blob/master/LICENSE)
