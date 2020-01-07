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
export default {
  components: {
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
    envVariables: Array
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
        parameters += this.parameters[index].parameter + this.parameters[index].value + ' '
      }
      var envVariables = ''
      for (var envIndex in this.envVariables) {
        envVariables += this.envVariables[envIndex].envVariable + this.envVariables[envIndex].value + ' '
      }
      return this.host + ' ' + this.convertResource(this.resource) + ' ' + envVariables + ' ' + this.command + ' ' + parameters
    }
  },

  watch: {
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
        }
      }
    },

    deleteParameter: function (id) {
      for (var index in this.parameters) {
        if (this.parameters[index].id === id) {
          this.parameters.splice(index, 1)
        }
      }
    },

    changeEnvVariable: function (id, envVariable, value) {
      for (var index in this.envVariables) {
        if (this.envVariables[index].id === id) {
          this.envVariables[index].envVariable = envVariable
          this.envVariables[index].value = value
        }
      }
    },

    deleteEnvVariable: function (id) {
      for (var index in this.envVariables) {
        if (this.envVariables[index].id === id) {
          this.envVariables.splice(index, 1)
        }
      }
    },

    updateLine: function () {
      this.$emit('changeLine', this.newHost, this.newResource, this.newCommand, this.newParameters, this.newEnvVariables)
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
