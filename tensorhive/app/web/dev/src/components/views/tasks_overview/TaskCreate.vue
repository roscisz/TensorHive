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
          :command="line.command"
          :parameters="line.parameters"
          @changeLine="changeLine(line.id, ...arguments)"
          @deleteLine="deleteLine(line.id)"
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
          envVariableIds: 0
        }
      ],
      show: false
    }
  },

  watch: {
    showModal () {
      this.show = this.showModal
    },
    show () {
      if (this.show === false) this.close()
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
        for (var envIndex in line.envVariables) {
          var envVariable = line.envVariables[envIndex]
          command += ' ' + envVariable.envVariable + ' ' + envVariable.value
        }
        command += ' ' + line.command
        for (var parameterIndex in line.parameters) {
          var parameter = line.parameters[parameterIndex]
          command += ' ' + parameter.parameter + ' ' + parameter.value
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

    addParameter: function () {
      for (var line in this.lines) {
        var parameter = {
          id: this.lines[line].parameterIds,
          parameter: this.newParameter,
          value: ''
        }
        this.lines[line].parameterIds++
        this.lines[line].parameters.push(parameter)
      }
    },

    addEnvVariable: function () {
      for (var line in this.lines) {
        var envVariable = {
          id: this.lines[line].envVariableIds,
          envVariable: this.newParameter,
          value: ''
        }
        this.lines[line].envVariableIds++
        this.lines[line].envVariables.push(envVariable)
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
          envVariables: newEnvVariables
        }
        this.linesIds++
        this.lines.push(line)
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
        ]
      }
      this.linesIds++
      this.lines.push(line)
    },

    changeLine: function (id, host, resource, command, parameters, envVariables) {
      for (var index in this.lines) {
        if (this.lines[index].id === id) {
          this.lines[index].host = host
          this.lines[index].resource = resource
          this.lines[index].command = command
          this.lines[index].parameters = parameters
          this.lines[index].envVariables = envVariables
        }
      }
    },

    deleteLine: function (id) {
      for (var index in this.lines) {
        if (this.lines[index].id === id) {
          this.lines.splice(index, 1)
        }
      }
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
