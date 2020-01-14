<template>
  <div>
    <v-layout align-center justify-center>
      <div class="task-preview">
        {{taskPreview}}
      </div>
    </v-layout>
    <v-layout align-center justify-start>
      <v-select
        class="task-select"
        :items="hostnames"
        label="Hostname"
        small
        v-model="newHost"
      ></v-select>
      <span class="space"/>
      <v-select
        class="task-select"
        :items="hostResources"
        label="Resource"
        small
        v-model="newResource"
      ></v-select>
      <span class="space"/>
      <v-layout align-center justify-start>
        <TaskLineTfConfig
          v-if="newEnableTfConfig"
          :value="tfConfig"
          :port="tfConfigPort"
          :task-type="tfConfigTaskType"
          :task-index="tfConfigTaskIndex"
          :tf-cluster="tfCluster"
          :enable-smart-tf-config="enableSmartTfConfig"
          @changeTfConfig="changeTfConfig(...arguments)"
          @deleteTfConfig="deleteTfConfig()"
          @updateTfConfigPort="updateTfConfigPort(...arguments)"
          @updateTfConfigTaskType="updateTfConfigTaskType(...arguments)"
          @updateTfConfigTaskIndex="updateTfConfigTaskIndex(...arguments)"
        />
      </v-layout>
      <span class="space"/>
      <v-layout align-center justify-start>
        <TaskLineEnvVariable
          class="task-input"
          v-for="envVariable in envVariables"
          :key="envVariable.id"
          :envVariable="envVariable.envVariable"
          :value="envVariable.value"
          @changeEnvVariable="changeEnvVariable(envVariable.id, ...arguments)"
          @deleteEnvVariable="deleteEnvVariable(envVariable.id)"
        />
      </v-layout>
      <span class="space"/>
      <v-text-field
        class="task-input"
        label="Command"
        small
        v-model="newCommand"
      ></v-text-field>
      <span class="space"/>
      <v-layout align-center justify-start>
        <TaskLineParameter
          class="task-input"
          v-for="parameter in parameters"
          :key="parameter.id"
          :parameter="parameter.parameter"
          :value="parameter.value"
          @changeParameter="changeParameter(parameter.id, ...arguments)"
          @deleteParameter="deleteParameter(parameter.id)"
        />
      </v-layout>
      <v-btn
        color="error"
        small
        @click="removeMe()"
      >
        Remove task
      </v-btn>
    </v-layout>
  </div>
</template>

<script>
import TaskLineParameter from './TaskLineParameter.vue'
import TaskLineEnvVariable from './TaskLineEnvVariable.vue'
import TaskLineTfConfig from './TaskLineTfConfig'
export default {
  components: {
    TaskLineTfConfig,
    TaskLineParameter,
    TaskLineEnvVariable
  },

  props: {
    hostnames: Array,
    hosts: Object,
    host: String,
    resource: String,
    command: String,
    parameters: Array,
    staticParameters: Array,
    envVariables: Array,
    staticEnvVariables: Array,
    enableTfConfig: Boolean,
    tfConfig: String,
    tfConfigPort: String,
    tfConfigTaskType: String,
    tfConfigTaskIndex: Number,
    tfCluster: Object,
    enableSmartTfConfig: Boolean
  },

  data () {
    return {
      newHost: '',
      newResource: '',
      newEnvVariables: [
        {
          id: 0,
          envVariable: '',
          value: ''
        }
      ],
      newCommand: '',
      newParameters: [
        {
          id: 0,
          parameter: '',
          value: ''
        }
      ],
      newEnableTfConfig: false,
      newTfConfig: '',
      showModal: false
    }
  },

  created () {
    this.newHost = this.host
    this.newResource = this.resource
    this.newEnvVariables = this.envVariables
    this.envVariableIds = this.envVariables.length
    this.newCommand = this.command
    this.newParameters = this.parameters
    this.parameterIds = this.parameters.length
    this.newEnableTfConfig = this.enableTfConfig
    this.newTfConfig = this.tfConfig
  },

  computed: {
    hostResources () {
      if (this.newHost !== '') {
        return this.hosts[this.newHost].resources
      } else {
        return []
      }
    },
    taskPreview () {
      var parameters = ''
      for (var index in this.parameters) {
        var parameterNameLength = this.parameters[index].parameter.length
        if (this.parameters[index].parameter.charAt(parameterNameLength - 1) === ' ' ||
            this.parameters[index].parameter.charAt(parameterNameLength - 1) === '=') {
          parameters += this.parameters[index].parameter + this.parameters[index].value + ' '
        } else {
          parameters += this.parameters[index].parameter + ' ' + this.parameters[index].value + ' '
        }
      }
      var envVariables = ''
      if (this.newEnableTfConfig) {
        envVariables += 'TF_CONFIG=' + this.newTfConfig + ' '
      }
      for (var envIndex in this.envVariables) {
        envVariables += this.envVariables[envIndex].envVariable + '=' + this.envVariables[envIndex].value + ' '
      }
      return this.host + ' ' + this.convertResource(this.resource) + ' ' + envVariables + ' ' + this.command + ' ' + parameters
    }
  },

  watch: {
    parameters () {
      this.newParameters = this.parameters
    },
    envVariables () {
      this.newEnvVariables = this.envVariables
    },
    enableTfConfig () {
      this.newEnableTfConfig = this.enableTfConfig
    },
    tfConfig () {
      this.newTfConfig = this.tfConfig
    },
    newHost () {
      this.newResource = this.hosts[this.newHost].resources[0]
      this.updateLine()
    },
    newResource () {
      this.updateLine()
    },
    newCommand () {
      this.updateLine()
    },
    newParameters () {
      this.updateLine()
    },
    newEnvVariables () {
      this.updateLine()
    },
    newEnableTfConfig () {
      this.updateLine()
    },
    newTfConfig () {
      this.updateLine()
    }
  },

  methods: {
    convertResource (resource) {
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

    changeParameter: function (id, parameter, value) {
      for (var index in this.parameters) {
        if (this.parameters[index].id === id) {
          this.parameters[index].parameter = parameter
          this.parameters[index].value = value
          for (var staticParameterName of this.staticParameters) {
            if (parameter === staticParameterName) {
              this.$emit('staticParameterChanged', parameter, value)
            }
          }
        }
      }
    },

    deleteParameter: function (id) {
      for (var index in this.parameters) {
        if (this.parameters[index].id === id) {
          for (var staticParameterName of this.staticParameters) {
            if (this.parameters[index].parameter === staticParameterName) {
              this.$emit('staticParameterDeleted', staticParameterName)
            }
          }
          this.parameters.splice(index, 1)
        }
      }
    },

    changeEnvVariable: function (id, envVariable, value) {
      for (var index in this.envVariables) {
        if (this.envVariables[index].id === id) {
          this.envVariables[index].envVariable = envVariable
          this.envVariables[index].value = value
          for (var staticEnvVariableName of this.staticEnvVariables) {
            if (envVariable === staticEnvVariableName) {
              this.$emit('staticEnvVariableChanged', envVariable, value)
            }
          }
        }
      }
    },

    deleteEnvVariable: function (id) {
      for (var index in this.envVariables) {
        if (this.envVariables[index].id === id) {
          for (var staticEnvVariableName of this.staticEnvVariables) {
            if (this.envVariables[index].envVariable === staticEnvVariableName) {
              this.$emit('staticEnvVariableDeleted', staticEnvVariableName)
            }
          }
          this.envVariables.splice(index, 1)
        }
      }
    },

    changeTfConfig: function (value) {
      this.newTfConfig = value
    },

    deleteTfConfig: function () {
      this.$emit('updateTfConfigTaskType', '')
      this.newEnableTfConfig = false
      this.newTfConfig = ''
    },

    updateTfConfigPort: function (newPort) {
      this.$emit('updateTfConfigPort', newPort)
    },

    updateTfConfigTaskType: function (newTaskType) {
      this.$emit('updateTfConfigTaskType', newTaskType)
    },

    updateTfConfigTaskIndex: function (newTaskIndex) {
      this.$emit('updateTfConfigTaskIndex', newTaskIndex)
    },

    updateLine: function () {
      this.$emit('changeLine', this.newHost, this.newResource, this.newCommand, this.newParameters, this.newEnvVariables, this.newEnableTfConfig, this.newTfConfig)
    },

    removeMe: function () {
      this.$emit('deleteLine')
    }
  }
}
</script>

<style scoped>
.space{
  width: 5px;
}
.task-preview{
  background-color: #f8f9fa;
  border: 1px solid #eaecf0;
  max-width: max-content;
}
.task-select{
  max-width:200px;
}
.task-input{
  max-width:200px;
}
</style>
