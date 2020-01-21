<template>
  <v-dialog
    width="80vw"
    v-model="show"
  >
    <v-card>
      <v-card-text>
        <v-btn
          class="float-right-button"
          flat
          icon
          color="black"
          @click="close()"
        >
          <v-icon>close</v-icon>
        </v-btn>
        <span class="headline">Create tasks</span>
        <v-tooltip right>
          <template v-slot:activator="{ on }">
            <v-icon v-on="on">
              info
            </v-icon>
          </template>
          <span>CPU tasks can be run without making reservation.
            <br>When you want to create a GPU task, you must
            <br>first ensure that you are eligible to do so
            <br>(having active reservation for that GPU).
          </span>
        </v-tooltip>
        <v-switch
          class="float-right-button"
          v-model="enableSmartTfConfig"
          label="Smart TF_CONFIG"/>
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
          <v-btn
            color="info"
            block
            small
            @click="copyLine"
          >
            Add task
          </v-btn>
        </v-flex>
        <v-layout align-center justify-start>
          <v-text-field
            label="Parameter name"
            small
            class="parameter-name-input"
            v-model="newParameter"
          ></v-text-field>
          <v-btn
            color="info"
            round
            @click="addEnvVariable"
          >
            Add as ENV variable to all tasks
          </v-btn>
          <v-btn
            color="info"
            round
            @click="addParameter"
          >
            Add as parameter to all tasks
          </v-btn>
          <v-checkbox
            v-model="isNewFieldStatic"
            :label="`Static`"></v-checkbox>
        </v-layout>
      </v-card-text>
      <v-card-text>
        <v-layout align-center justify-end>
          <v-btn
            color="success"
            @click="addTasks"
          >
            Create all tasks
          </v-btn>
        </v-layout>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>

<script>
import api from '../../../api'
import TaskLine from './TaskLine.vue'
export default {
  components: {
    TaskLine
  },

  props: {
    showModal: Boolean,
    hostnames: Array,
    hosts: Object,
    actionFlag: Boolean,
    chosenTemplate: String
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
      show: false
    }
  },

  watch: {
    showModal () {
      this.show = this.showModal
    },
    show () {
      if (this.show === false) this.close()
      else {
        switch (this.chosenTemplate) {
          case 'tf1':
            this.emptyParametersAndEnvVariables()
            this.addParameter(undefined, '--ps_hosts=')
            this.addParameter(undefined, '--worker_hosts=')
            this.addParameter(undefined, '--job_name=')
            this.addParameter(undefined, '--task_index=')
            this.staticParameters = ['--ps_hosts=', '--worker_hosts=']
            break
          case 'tf2':
            this.emptyParametersAndEnvVariables()
            this.enableSmartTfConfig = true
            this.addEnvVariable(undefined, 'TF_CONFIG')
            break
          case 'torch':
            this.emptyParametersAndEnvVariables()
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
    }
  },

  methods: {
    close: function () {
      this.$emit('close')
    },

    addTasks: function () {
      for (var lineIndex in this.lines) {
        var line = this.lines[lineIndex]
        var command = this.convertResource(line.resource)
        if (line.enableTfConfig) {
          command += ' TF_CONFIG=' + line.tfConfig
        }
        for (var envIndex in line.envVariables) {
          var envVariable = line.envVariables[envIndex]
          command += ' ' + envVariable.envVariable + '=' + envVariable.value
        }
        command += ' ' + line.command
        for (var parameterIndex in line.parameters) {
          var parameter = line.parameters[parameterIndex]
          var parameterNameLength = parameter.parameter.length
          if (parameter.parameter.charAt(parameterNameLength - 1) === ' ' ||
              parameter.parameter.charAt(parameterNameLength - 1) === '=') {
            command += ' ' + parameter.parameter + parameter.value
          } else {
            command += ' ' + parameter.parameter + ' ' + parameter.value
          }
        }
        var task = {
          userId: this.$store.state.id,
          hostname: line.host,
          command: command
        }
        if (!this.actionFlag) {
          api
            .request('post', '/tasks', this.$store.state.accessToken, task)
            .then(response => {
              this.close()
              this.$emit('getTasks', false)
            })
        }
      }
    },

    addParameter: function (event, parameterName, parameterValue) {
      for (var line in this.lines) {
        var parameter = {
          id: this.lines[line].parameterIds,
          parameter: parameterName || this.newParameter,
          value: parameterValue || ''
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
      this.isNewFieldStatic = false
      this.staticParameters = []
      this.staticEnvVariables = []
      for (var lineIndex in this.lines) {
        this.lines[lineIndex].tfConfigTaskIndex = -1
        this.lines[lineIndex].tfConfigTaskType = ''
        this.lines[lineIndex].tfConfigPort = ''
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
.parameter-name-input{
  max-width: 150px;
}
</style>
