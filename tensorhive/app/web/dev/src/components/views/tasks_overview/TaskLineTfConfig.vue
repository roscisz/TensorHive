<template>
  <v-layout align-center justify-start>
    <TfConfigEdit
      :value="newValue"
      :show-modal="showModalTfConfigEdit"
      @close="showModalTfConfigEdit = false"
      @updateValue="updateValue(...arguments)"
    />
    <v-layout v-if="enableSmartTfConfig">
      <v-text-field
        class="tf-short"
        label="Port"
        small
        v-model="newPort"
      />
      <span class="space"/>
      <v-combobox
        class="tf-wide"
        label="Task type"
        v-model="newTaskType"
        :items="taskTypeItems"
      />
      <span class="space"/>
      <v-text-field
        class="tf-short"
        label="Index"
        type="number"
        hide-details
        single-line
        small
        v-if="newTaskIndex >= 0"
        v-model="newTaskIndex"
      />
    </v-layout>
    <v-btn
      v-else
      class="task-input"
      color="info"
      @click="showModalTfConfigEdit = true"
      round
      medium
    >
      TF_CONFIG
    </v-btn>
    <v-tooltip bottom color="red">
      <template v-slot:activator="{ on }">
        <v-btn
          color="indigo"
          fab
          dark
          small
          outline
          @click="removeMe()"
          class="remove-button remove-button-tf"
          v-on="on"
        >
          <v-icon dark>delete</v-icon>
        </v-btn>
      </template>
      <span>Delete TF_CONFIG</span>
    </v-tooltip>
  </v-layout>
</template>

<script>
import TfConfigEdit from './TfConfigEdit'
export default {
  components: {TfConfigEdit},

  name: 'TaskLineTfConfig',

  props: {
    value: String,
    port: String,
    taskType: String,
    taskIndex: Number,
    tfCluster: Object,
    enableSmartTfConfig: Boolean
  },

  data () {
    return {
      newValue: '',
      newPort: '',
      newTaskType: '',
      taskTypeItems: [
        'chief',
        'evaluator',
        'master',
        'ps',
        'worker'
      ],
      newTaskIndex: -1,
      localEnableSmartTfConfig: false,
      showModalTfConfigEdit: false
    }
  },

  created () {
    this.newValue = this.value
    this.newPort = this.port
    this.newTaskType = this.taskType
    this.newTaskIndex = this.taskIndex
    this.localEnableSmartTfConfig = this.enableSmartTfConfig
  },

  watch: {
    value () {
      this.newValue = this.value
    },
    port () {
      this.newPort = this.port
    },
    taskType () {
      this.newTaskType = this.taskType
    },
    taskIndex () {
      this.newTaskIndex = this.taskIndex
    },
    tfCluster () {
      if (this.newTaskIndex >= 0) {
        var value = {
          cluster: this.tfCluster,
          task: {
            type: this.newTaskType,
            index: this.newTaskIndex
          }
        }
        this.updateValue(
          '\'' + JSON.stringify(value).split('"').join('\\"') + '\''
        )
      } else {
        this.updateValue('')
      }
    },
    enableSmartTfConfig () {
      this.localEnableSmartTfConfig = this.enableSmartTfConfig
    },
    newValue () {
      this.$emit('changeTfConfig', this.newValue)
    },
    newPort () {
      this.$emit('updateTfConfigPort', this.newPort)
    },
    newTaskType () {
      this.$emit('updateTfConfigTaskType', this.newTaskType)
    },
    newTaskIndex () {
      if (isNaN(parseInt(this.newTaskIndex))) {
        this.newTaskIndex = this.taskIndex
      } else {
        // FIXME there is edge case when index is 0 and it's the only task of this type - it occurs when you change by button
        this.$emit('updateTfConfigTaskIndex', parseInt(this.newTaskIndex))
      }
    }
  },

  methods: {
    removeMe: function () {
      this.$emit('deleteTfConfig')
    },

    updateValue: function (newValue) {
      this.newValue = newValue
    }
  }
}
</script>

<style scoped>
  .remove-button{
    max-width:25px;
    max-height:25px;
    min-width:25px;
    min-height:25px;
    margin-left:-25px;
  }
  .remove-button-tf{
    margin-left:-5px;
  }
  .task-input{
    max-width:200px;
  }
  .tf-short{
    max-width:50px;
  }
  .tf-wide{
    max-width:100px;
  }
</style>
