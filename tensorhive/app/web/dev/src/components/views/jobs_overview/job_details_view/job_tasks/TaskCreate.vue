<template>
  <v-dialog width="80vw" v-model="showModal">
    <template v-slot:activator="{ on }">
      <v-btn v-on="on" color="primary" @click="$emit('open')">Add Tasks</v-btn>
    </template>
    <v-card>
      <v-card-text>
        <v-btn
          class="float-right-button"
          flat
          icon
          color="black"
          @click="close"
        >
          <v-icon>close</v-icon>
        </v-btn>
        <span
          v-if="editingTasks && editingTasks.length > 0"
          class="headline"
        >Edit tasks</span>
        <span v-else class="headline">Create tasks</span>
        <v-tooltip right>
          <template v-slot:activator="{ on }">
            <v-icon v-on="on">info</v-icon>
          </template>
          <span>
            CPU tasks can be run without making reservation.
            <br />When you want to create a GPU task, you must
            <br />first ensure that you are eligible to do so
            <br />(having active reservation for that GPU).
          </span>
        </v-tooltip>
        <v-switch
          class="float-right-button"
          v-if="chosenTemplate === 'tf2'"
          v-model="enableSmartTfConfig"
          label="Smart TF_CONFIG"
        />
      </v-card-text>
      <v-card-text>
        <TaskLine
          v-for="line in lines"
          :key="line.id"
          :hostnames="hostnames"
          :hosts="hosts"
          :host="line.host"
          :resource="line.resource"
          :envVariables="line.envVariables"
          :staticEnvVariables="staticEnvVariables"
          :command="line.command"
          :parameters="line.parameters"
          :staticParameters="staticParameters"
          :enable-tf-config="line.enableTfConfig"
          :tf-config="line.tfConfig"
          :tf-config-port="line.tfConfigPort"
          :tf-config-task-type="line.tfConfigTaskType"
          :tf-config-task-index="line.tfConfigTaskIndex"
          :tf-cluster="tfCluster"
          :enable-smart-tf-config="enableSmartTfConfig"
          @changeLine="changeLine(line.id, ...arguments)"
          @deleteLine="deleteLine(line.id)"
          @staticParameterChanged="staticParameterChanged(line.id, ...arguments)"
          @psWorkerParameterChanged="updatePsWorkerHosts(-1, '')"
          @staticEnvVariableChanged="staticEnvVariableChanged(line.id, ...arguments)"
          @staticParameterDeleted="staticParameterDeleted(line.id, ...arguments)"
          @staticEnvVariableDeleted="staticEnvVariableDeleted(line.id, ...arguments)"
          @updateTfConfigPort="updateTfConfigPort(line.id, ...arguments)"
          @updateTfConfigTaskType="updateTfConfigTaskType(line.id, ...arguments)"
          @updateTfConfigTaskIndex="updateTfConfigTaskIndex(line.id, ...arguments)"
        />
      </v-card-text>
      <v-card-text>
        <v-flex xs12>
          <v-btn color="primary" block small @click="copyLine">Add task</v-btn>
        </v-flex>
        <v-layout align-center justify-start>
          <v-text-field
            label="Parameter name"
            small
            class="parameter-name-input"
            v-model="newParameter"
          ></v-text-field>
          <v-btn
            color="primary"
            @click="addEnvVariable"
          >Add as ENV variable to all tasks</v-btn>
          <v-btn
            color="primary"
            @click="addParameter"
          >Add as parameter to all tasks</v-btn>
          <v-checkbox v-model="isNewFieldStatic" :label="`Static`"></v-checkbox>
        </v-layout>
      </v-card-text>
      <v-card-text>
        <v-layout align-center justify-end>
          <v-btn color="primary" @click="saveTasks">
            <span v-if="editingTasks && editingTasks.length > 0">Edit all tasks</span>
            <span v-else>Create all tasks</span>
          </v-btn>
        </v-layout>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>

<script>
import api from '../../../../../api'
import TaskLine from './TaskLine.vue'
export default {
  components: {
    TaskLine
  },
  props: {
    showModal: {
      type: Boolean,
      default: false
    },
    chosenTemplate: {
      type: String,
      default: ''
    },
    selectedTasks: {
      type: Array,
      default () {
        return []
      }
    },
    editingTasks: {
      type: Array,
      default () {
        return []
      }
    }
  },
  data () {
    return {
      newParameter: '',
      linesIds: 1,
      lines: [
        {
          id: 0,
          host: '',
          resource: '',
          command: '',
          parameters: [
          ],
          envVariables: [
          ],
          parameterIds: 0,
          envVariableIds: 0,
          enableTfConfig: false,
          tfConfig: '',
          tfConfigPort: '',
          tfConfigTaskType: '',
          tfConfigTaskIndex: -1
        }
      ],
      tfCluster: {},
      staticParameters: [],
      staticEnvVariables: [],
      isNewFieldStatic: false,
      enableSmartTfConfig: false,
      show: false,
      hosts: {},
      hostname: []
    }
  },
  mounted () {
    api
      .request('get', '/nodes/metrics', this.$store.state.accessToken)
      .then(response => {
        this.convertHostsInfo(response.data)
      })
  },
  watch: {
    showModal () {
      if (this.showModal === false) {
        this.lines = [
          {
            id: 0,
            host: '',
            resource: '',
            command: '',
            parameters: [
            ],
            envVariables: [
            ],
            parameterIds: 0,
            envVariableIds: 0,
            enableTfConfig: false,
            tfConfig: '',
            tfConfigPort: '',
            tfConfigTaskType: '',
            tfConfigTaskIndex: -1
          }
        ]
        this.close()
      } else if (this.chosenTemplate !== '') {
        this.emptyParametersAndEnvVariables()
        switch (this.chosenTemplate) {
          case 'tf1':
            this.addParameter(undefined, '--ps_hosts=')
            this.addParameter(undefined, '--worker_hosts=')
            this.addParameter(undefined, '--job_name=', 'worker')
            this.addParameter(undefined, '--task_index=')
            this.staticParameters = ['--ps_hosts=', '--worker_hosts=']
            break
          case 'tf2':
            this.enableSmartTfConfig = true
            this.addEnvVariable(undefined, 'TF_CONFIG')
            break
          case 'torch':
            this.addParameter(undefined, '--init-method=')
            this.addParameter(undefined, '--backend=', 'gloo')
            this.addParameter(undefined, '--rank=')
            this.addParameter(undefined, '--world-size=')
            this.staticParameters = ['--init-method=', '--backend=', '--world-size=']
            break
          default:
            break
        }
      }
    },
    selectedTasks () {
      if (this.selectedTasks && this.selectedTasks.length) {
        let newLines = []
        let ids = 0
        for (let task of this.selectedTasks) {
          let parsedCommand = this.parseCommand(task)
          let parsedEnvVariables = this.parseSegments(task, 'envs')
          let parsedParams = this.parseSegments(task, 'params')
          newLines.push({
            id: ids,
            host: task.hostname,
            resource: parsedCommand.resource,
            command: parsedCommand.command,
            parameters: parsedParams.params,
            envVariables: parsedEnvVariables.envs,
            parameterIds: parsedParams.ids,
            envVariableIds: parsedEnvVariables.ids,
            enableTfConfig: false,
            tfConfig: '',
            tfConfigPort: '',
            tfConfigTaskType: '',
            tfConfigTaskIndex: -1
          })
          ids++
        }
        this.lines = newLines
        this.linesIds = ids
      }
    },
    editingTasks () {
      if (this.editingTasks && this.editingTasks.length) {
        let newLines = []
        let ids = 0
        for (let task of this.editingTasks) {
          let parsedCommand = this.parseCommand(task)
          let parsedEnvVariables = this.parseSegments(task, 'envs')
          let parsedParams = this.parseSegments(task, 'params')
          newLines.push({
            id: ids,
            taskId: task.id,
            host: task.hostname,
            resource: parsedCommand.resource,
            command: parsedCommand.command,
            parameters: parsedParams.params,
            envVariables: parsedEnvVariables.envs,
            parameterIds: parsedParams.ids,
            envVariableIds: parsedEnvVariables.ids,
            enableTfConfig: false,
            tfConfig: '',
            tfConfigPort: '',
            tfConfigTaskType: '',
            tfConfigTaskIndex: -1
          })
          ids++
        }
        this.lines = newLines
        this.linesIds = ids
      }
    }
  },

  methods: {
    close () {
      this.$emit('close')
    },
    parseCommand (task) {
      const match = /CUDA_VISIBLE_DEVICES=(\d*)/.exec(task.command)

      if (match && match[1]) {
        return {
          resource: { name: `GPU${match[1]}`, id: Number(match[1]) },
          command: task.command.replace(/CUDA_VISIBLE_DEVICES=(\d*) /, '')
        }
      }

      return {
        resource: { name: 'CPU', id: null },
        command: task.command.replace('CUDA_VISIBLE_DEVICES=', '')
      }
    },
    parseSegments (task, type) {
      let ids = 0
      let newSegments = []
      if (task.cmdsegments && task.cmdsegments[type] && task.cmdsegments[type].length) {
        for (let segment of task.cmdsegments[type]) {
          segment.id = ids
          newSegments.push(segment)
          ids++
        }
        return {
          [type]: newSegments,
          ids: ids
        }
      } else {
        return {
          [type]: [],
          ids: 0
        }
      }
    },
    convertHostsInfo (hostsInfo) {
      var hosts = {}
      for (var hostname in hostsInfo) {
        var host = hostsInfo[hostname]
        var resources = ['CPU']
        for (var gpuUUID in host.GPU) {
          resources.push('GPU' + host.GPU[gpuUUID].index)
        }
        hosts[hostname] = { resources: resources }
      }
      this.hosts = hosts
      this.hostnames = Object.keys(hosts)
    },

    saveTasks () {
      let tasks = []
      for (var lineIndex in this.lines) {
        let line = this.lines[lineIndex]
        let task = {
          hostname: line.host,
          cmdsegments: {
            envs: this.formatSegments(line.envVariables),
            params: this.formatSegments(line.parameters, false)
          },
          command: this.convertResource(line.resource) + ' ' + line.command,
          id: line.taskId ? line.taskId : -1
        }
        tasks.push(task)
      }
      if (this.editingTasks && this.editingTasks.length > 0) {
        this.$emit('edit', tasks)
      } else {
        this.$emit('add', tasks)
      }
    },

    formatSegments (segments, envVariable = true) {
      let formatedVariables = []
      for (let segment of segments) {
        formatedVariables.push({
          name: envVariable ? segment.envVariable : segment.parameter,
          value: segment.value
        })
      }
      return formatedVariables
    },

    addParameter (event, parameterName, parameterValue) {
      let taskIndex = 0
      for (var line in this.lines) {
        var parameter = {
          id: this.lines[line].parameterIds,
          parameter: parameterName || this.newParameter,
          value: parameterValue || ''
        }
        if ((this.chosenTemplate === 'tf1' && parameterName === '--task_index=') ||
          (this.chosenTemplate === 'torch' && parameterName === '--rank=') ||
          (this.chosenTemplate === 'torch' && parameterName === '--world-size=')) {
          if (parameterName === '--world-size=') {
            taskIndex++
            parameter.value = taskIndex.toString()
          } else {
            parameter.value = taskIndex.toString()
            taskIndex++
          }
        }
        this.lines[line].parameterIds++
        this.lines[line].parameters.push(parameter)
      }
      if (this.isNewFieldStatic) {
        this.staticParameters.push(parameterName || this.newParameter)
      }
    },

    addEnvVariable: function (event, variableName, variableValue) {
      var newName = variableName || this.newParameter
      if (newName.charAt(newName.length - 1) === '=') {
        newName = newName.substring(0, newName.length - 1)
      }
      var line
      if (newName === 'TF_CONFIG') {
        this.chosenTemplate = 'tf2'
        for (line in this.lines) {
          this.lines[line].enableTfConfig = true
          this.lines[line].tfConfig = ''
        }
        let machinePorts = {}
        for (line in this.lines) {
          const host = this.lines[line].host
          this.updateTfConfigTaskType(this.lines[line].id, 'worker')
          if (host) {
            if (machinePorts.hasOwnProperty(host)) {
              this.updateTfConfigPort(this.lines[line].id, machinePorts[host].toString())
              machinePorts[host]++
            } else {
              this.updateTfConfigPort(this.lines[line].id, '2222')
              machinePorts[host] = 2223
            }
          }
        }
      } else {
        for (line in this.lines) {
          var envVariable = {
            id: this.lines[line].envVariableIds,
            envVariable: newName,
            value: variableValue || ''
          }
          this.lines[line].envVariableIds++
          this.lines[line].envVariables.push(envVariable)
        }
        if (this.isNewFieldStatic) {
          this.staticEnvVariables.push(newName)
        }
      }
    },

    copyLine: function () {
      if (this.lines.length === 0) {
        this.addLine()
      } else {
        var lineToCopy = this.lines[this.lines.length - 1]
        var parametersToCopy = lineToCopy.parameters
        var newParameters = []
        for (var index in parametersToCopy) {
          var parameterToCopy = parametersToCopy[index]
          var newParameter = {
            id: index,
            parameter: parameterToCopy.parameter,
            value: parameterToCopy.value
          }
          if ((this.chosenTemplate === 'tf1' && newParameter.parameter === '--task_index=') ||
            (this.chosenTemplate === 'torch' && newParameter.parameter === '--rank=') ||
            (this.chosenTemplate === 'torch' && newParameter.parameter === '--world-size=')) {
            newParameter.value = (parseInt(newParameter.value) + 1).toString()
          }
          newParameters.push(newParameter)
        }

        var envVariablesToCopy = lineToCopy.envVariables
        var newEnvVariables = []
        for (var EnvIndex in envVariablesToCopy) {
          var envVariableToCopy = envVariablesToCopy[EnvIndex]
          var newEnvVariable = {
            id: EnvIndex,
            envVariable: envVariableToCopy.envVariable,
            value: envVariableToCopy.value
          }
          newEnvVariables.push(newEnvVariable)
        }
        var line = {
          id: this.linesIds,
          host: lineToCopy.host,
          resource: lineToCopy.resource,
          command: lineToCopy.command,
          parameters: newParameters,
          envVariables: newEnvVariables,
          enableTfConfig: lineToCopy.enableTfConfig,
          tfConfig: lineToCopy.tfConfig,
          tfConfigPort: '',
          tfConfigTaskType: '',
          tfConfigTaskIndex: -1
        }
        this.linesIds++
        this.lines.push(line)

        if (lineToCopy.enableTfConfig && this.enableSmartTfConfig) {
          this.updateTfConfigTaskType(line.id, lineToCopy.tfConfigTaskType)
          if (line.host) {
            let machineHosts = {}
            machineHosts[line.host] = 2221
            for (var lineIndex in this.lines) {
              if (this.lines[lineIndex].host && this.lines[lineIndex].tfConfigPort) {
                if (machineHosts.hasOwnProperty(this.lines[lineIndex].host)) {
                  machineHosts[this.lines[lineIndex].host] = Math.max(
                    machineHosts[this.lines[lineIndex].host],
                    parseInt(this.lines[lineIndex].tfConfigPort)
                  )
                } else {
                  machineHosts[this.lines[lineIndex].host] = 2221
                }
              }
            }
            this.updateTfConfigPort(line.id, (machineHosts[line.host] + 1).toString())
          }
        }
      }
    },

    addLine: function () {
      var line = {
        id: this.linesIds,
        host: '',
        resource: '',
        command: '',
        envVariables: [
        ],
        parameters: [
        ],
        parameterIds: 0,
        envVariableIds: 0,
        enableTfConfig: false,
        tfConfig: '',
        tfConfigPort: '',
        tfConfigTaskType: '',
        tfConfigTaskIndex: -1
      }
      this.linesIds++
      this.lines.push(line)
    },

    changeLine: function (id, host, resource, command, parameters, envVariables, enableTfConfig, tfConfig) {
      for (var index in this.lines) {
        if (this.lines[index].id === id) {
          if (host !== this.lines[index].host && enableTfConfig && this.enableSmartTfConfig) {
            this.updateTfConfigHost(id, host)
          }
          if (this.chosenTemplate === 'tf1') {
            this.updatePsWorkerHosts(index, host)
          }
          this.lines[index].host = host
          this.lines[index].resource = resource
          this.lines[index].command = command
          this.lines[index].parameters = parameters
          this.lines[index].envVariables = envVariables
          this.lines[index].enableTfConfig = enableTfConfig
          this.lines[index].tfConfig = tfConfig
        }
      }
    },

    deleteLine: function (id) {
      for (var index in this.lines) {
        if (this.lines[index].id === id) {
          if (this.lines[index].enableTfConfig && this.enableSmartTfConfig) {
            this.updateTfConfigTaskType(this.lines[index].id, '')
          }
          this.lines.splice(index, 1)
        }
      }
    },

    staticParameterChanged: function (id, parameter, value) {
      for (var index in this.lines) {
        if (this.lines[index].id !== id) {
          for (var parameterIndex in this.lines[index].parameters) {
            if (this.lines[index].parameters[parameterIndex].parameter === parameter) {
              this.lines[index].parameters[parameterIndex].value = value
            }
          }
        }
      }
    },

    staticParameterDeleted: function (id, parameter) {
      var staticIndex = this.staticParameters.indexOf(parameter)
      if (staticIndex !== -1) this.staticParameters.splice(staticIndex, 1)
      for (var index in this.lines) {
        if (this.lines[index].id !== id) {
          for (var parameterIndex in this.lines[index].parameters) {
            if (this.lines[index].parameters[parameterIndex].parameter === parameter) {
              this.lines[index].parameters.splice(parameterIndex, 1)
            }
          }
        }
      }
    },

    staticEnvVariableChanged: function (id, variable, value) {
      for (var index in this.lines) {
        if (this.lines[index].id !== id) {
          for (var variableIndex in this.lines[index].envVariables) {
            if (this.lines[index].envVariables[variableIndex].envVariable === variable) {
              this.lines[index].envVariables[variableIndex].value = value
            }
          }
        }
      }
    },

    staticEnvVariableDeleted: function (id, variable) {
      var staticIndex = this.staticEnvVariables.indexOf(variable)
      if (staticIndex !== -1) this.staticEnvVariables.splice(staticIndex, 1)
      for (var index in this.lines) {
        if (this.lines[index].id !== id) {
          for (var variableIndex in this.lines[index].envVariables) {
            if (this.lines[index].envVariables[variableIndex].envVariable === variable) {
              this.lines[index].envVariables.splice(variableIndex, 1)
            }
          }
        }
      }
    },

    updatePsWorkerHosts: function (index, host) {
      var psHosts = []
      var workerHosts = []
      var currentPort = 2222

      for (let line in this.lines) {
        let currLine = this.lines[line]
        let jobName = ''
        for (let paramIndex in currLine.parameters) {
          if (currLine.parameters[paramIndex].parameter === '--job_name=') {
            jobName = currLine.parameters[paramIndex].value
          }
        }
        for (let paramIndex in currLine.parameters) {
          if (currLine.parameters[paramIndex].parameter === '--task_index=') {
            let lineHost = ''
            if (line === index) {
              lineHost = host
            } else {
              lineHost = currLine.host
            }
            if (jobName === 'worker') {
              workerHosts[currLine.parameters[paramIndex].value] = lineHost + ':' + currentPort.toString()
              currentPort++
            } else if (jobName === 'ps') {
              psHosts[currLine.parameters[paramIndex].value] = lineHost + ':' + currentPort.toString()
              currentPort++
            }
          }
        }
      }

      var psHostsParam = ''
      var workerHostsParam = ''

      for (let pHost in psHosts) {
        psHostsParam += psHosts[pHost] + ','
      }
      psHostsParam = psHostsParam.replace(/,\s*$/, '')
      for (let wHost in workerHosts) {
        workerHostsParam += workerHosts[wHost] + ','
      }
      workerHostsParam = workerHostsParam.replace(/,\s*$/, '')

      for (let line in this.lines) {
        for (let paramIndex in this.lines[line].parameters) {
          if (this.lines[line].parameters[paramIndex].parameter === '--ps_hosts=') {
            this.lines[line].parameters[paramIndex].value = psHostsParam
          } else if (this.lines[line].parameters[paramIndex].parameter === '--worker_hosts=') {
            this.lines[line].parameters[paramIndex].value = workerHostsParam
          }
        }
      }
    },

    updateTfConfigHost: function (id, host) {
      // search for line
      var lineIndex
      for (lineIndex in this.lines) {
        if (this.lines[lineIndex].id === id) {
          break
        }
      }

      // set new config port
      let machineHosts = {}
      machineHosts[host] = 2221
      for (var line in this.lines) {
        if (this.lines[line].id !== id && this.lines[line].host && this.lines[line].tfConfigPort) {
          if (machineHosts.hasOwnProperty(this.lines[line].host)) {
            machineHosts[this.lines[line].host] = Math.max(
              machineHosts[this.lines[line].host],
              parseInt(this.lines[line].tfConfigPort)
            )
          } else {
            machineHosts[this.lines[line].host] = 2221
          }
        }
      }
      this.lines[lineIndex].tfConfigPort = (machineHosts[host] + 1).toString()

      // check if given line has taskIndex set
      var taskIndex = this.lines[lineIndex].tfConfigTaskIndex
      if (taskIndex !== -1) {
        var taskType = this.lines[lineIndex].tfConfigTaskType
        this.tfCluster[taskType][taskIndex] = host + ':' + this.lines[lineIndex].tfConfigPort
        this.tfCluster.__ob__.dep.notify()
      }
    },

    updateTfConfigPort: function (id, port) {
      // search for line
      var lineIndex
      for (lineIndex in this.lines) {
        if (this.lines[lineIndex].id === id) {
          break
        }
      }

      if (!this.lines[lineIndex].enableTfConfig || !this.enableSmartTfConfig) {
        return
      }

      this.lines[lineIndex].tfConfigPort = port

      // check if given line has taskIndex set
      var taskIndex = this.lines[lineIndex].tfConfigTaskIndex
      if (taskIndex !== -1) {
        var taskType = this.lines[lineIndex].tfConfigTaskType
        this.tfCluster[taskType][taskIndex] = this.lines[lineIndex].host + ':' + this.lines[lineIndex].tfConfigPort
        this.tfCluster.__ob__.dep.notify()
      }
    },

    updateTfConfigTaskType: function (id, taskType) {
      // search for line
      var lineIndex
      for (lineIndex in this.lines) {
        if (this.lines[lineIndex].id === id) {
          break
        }
      }

      if (!this.lines[lineIndex].enableTfConfig || !this.enableSmartTfConfig) {
        return
      }

      // remove from old list of cluster tasks
      var oldTaskType = this.lines[lineIndex].tfConfigTaskType
      if (oldTaskType && oldTaskType.length !== 0) {
        var oldTaskIndex = this.lines[lineIndex].tfConfigTaskIndex
        this.tfCluster[oldTaskType].splice(oldTaskIndex, 1)
        if (this.tfCluster[oldTaskType].length !== 0) {
          for (var otherLineIndex in this.lines) {
            if (this.lines[otherLineIndex].tfConfigTaskType === oldTaskType &&
              this.lines[otherLineIndex].tfConfigTaskIndex > oldTaskIndex) {
              this.lines[otherLineIndex].tfConfigTaskIndex -= 1
            }
          }
        } else {
          delete this.tfCluster[oldTaskType]
        }
      }

      // Assign new taskType and taskIndex
      if (!taskType || taskType.length === 0) {
        this.lines[lineIndex].tfConfigTaskType = taskType
        this.lines[lineIndex].tfConfigTaskIndex = -1
      } else {
        // check if there is a list with new taskType
        if (!this.tfCluster.hasOwnProperty(taskType)) {
          this.tfCluster[taskType] = []
        }

        this.lines[lineIndex].tfConfigTaskType = taskType
        this.lines[lineIndex].tfConfigTaskIndex = this.tfCluster[taskType].length

        this.tfCluster[taskType].push(this.lines[lineIndex].host + ':' + this.lines[lineIndex].tfConfigPort)
      }
      this.tfCluster.__ob__.dep.notify()
    },

    updateTfConfigTaskIndex: function (id, newTaskIndex) {
      // search for line
      var lineIndex
      for (lineIndex in this.lines) {
        if (this.lines[lineIndex].id === id) {
          break
        }
      }

      if (!this.lines[lineIndex].enableTfConfig || !this.enableSmartTfConfig ||
        newTaskIndex === this.lines[lineIndex].tfConfigTaskIndex) {
        return
      }

      var taskType = this.lines[lineIndex].tfConfigTaskType
      var oldTaskIndex = this.lines[lineIndex].tfConfigTaskIndex
      if (this.tfCluster[taskType].length <= newTaskIndex) {
        newTaskIndex = 0
      } else if (newTaskIndex < 0) {
        newTaskIndex = this.tfCluster[taskType].length - 1
      }
      if (newTaskIndex === this.lines[lineIndex].tfConfigTaskIndex) {
        return
      }

      var value = this.tfCluster[taskType][oldTaskIndex]
      this.tfCluster[taskType].splice(oldTaskIndex, 1)
      for (var otherLineIndex in this.lines) {
        if (this.lines[otherLineIndex].tfConfigTaskType === taskType &&
          this.lines[otherLineIndex].tfConfigTaskIndex > oldTaskIndex) {
          this.lines[otherLineIndex].tfConfigTaskIndex -= 1
        }
        if (this.lines[otherLineIndex].tfConfigTaskType === taskType &&
          this.lines[otherLineIndex].tfConfigTaskIndex >= newTaskIndex) {
          this.lines[otherLineIndex].tfConfigTaskIndex += 1
        }
      }
      this.tfCluster[taskType].splice(newTaskIndex, 0, value)
      this.lines[lineIndex].tfConfigTaskIndex = newTaskIndex
      this.tfCluster.__ob__.dep.notify()
    },

    convertResource: function (resource) {
      if (resource !== '' && resource !== null) {
        if (resource === 'CPU') {
          return 'CUDA_VISIBLE_DEVICES='
        } else {
          return 'CUDA_VISIBLE_DEVICES=' + resource[3]
        }
      } else {
        return ''
      }
    },

    emptyParametersAndEnvVariables: function () {
      this.enableSmartTfConfig = false
      this.isNewFieldStatic = false
      this.staticParameters = []
      this.staticEnvVariables = []
      for (var lineIndex in this.lines) {
        this.lines[lineIndex].tfConfigTaskIndex = 0
        this.lines[lineIndex].tfConfigTaskType = ''
        this.lines[lineIndex].tfConfigPort = ''
        this.lines[lineIndex].enableTfConfig = false
        this.lines[lineIndex].parameters = []
        this.lines[lineIndex].parameterIds = 0
        this.lines[lineIndex].envVariables = []
        this.lines[lineIndex].envVariableIds = 0
      }
      this.tfCluster = {}
    }
  }
}
</script>

<style scoped>
  .float-right-button {
    float: right;
  }
  .parameter-name-input {
    max-width: 150px;
  }
</style>
