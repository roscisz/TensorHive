<template>
  <v-layout align-center justify-start v-if="newEnvVariable==='TF_CONFIG'">
    <TfConfigEdit
      :value="newValue"
      :show-modal="showModalTfConfigEdit"
      @close="showModalTfConfigEdit = false"
      @updateValue="updateValue(...arguments)"
    />
    <v-btn
      color="info"
      @click="showModalTfConfigEdit = true"
      round
      medium
    >
      TF_CONFIG
    </v-btn>
    <v-btn
      color="indigo"
      fab
      dark
      small
      outline
      @click="removeMe()"
      class="remove-button remove-button-tf"
    >
      <v-icon dark>delete</v-icon>
    </v-btn>
  </v-layout>
  <v-layout align-center justify-start v-else>
    <v-text-field
      class="task-input"
      :label="newEnvVariable"
      small
      v-model="newValue"
    ></v-text-field>
    <v-btn
      color="indigo"
      fab
      dark
      small
      outline
      @click="removeMe()"
      class="remove-button"
    >
      <v-icon dark>delete</v-icon>
    </v-btn>
  </v-layout>
</template>

<script>
import TfConfigEdit from './TfConfigEdit'
export default {
  components: {TfConfigEdit},
  props: {
    envVariable: String,
    value: String
  },

  data () {
    return {
      newEnvVariable: '',
      newValue: '',
      showModalTfConfigEdit: false
    }
  },

  created () {
    this.newEnvVariable = this.envVariable
    this.newValue = this.value
  },

  watch: {
    value () {
      this.newValue = this.value
    },
    newEnvVariable () {
      this.$emit('changeEnvVariable', this.newEnvVariable, this.newValue)
    },
    newValue () {
      this.$emit('changeEnvVariable', this.newEnvVariable, this.newValue)
    }
  },

  methods: {
    removeMe: function () {
      this.$emit('deleteEnvVariable')
    },

    updateValue: function (newValue) {
      this.newValue = newValue
    }
  }
}
</script>
<style>
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
</style>
