<template>
  <v-layout align-center justify-start>
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
export default {
  props: {
    envVariable: String,
    value: String
  },

  data () {
    return {
      newEnvVariable: '',
      newValue: ''
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
.task-input{
  max-width:200px;
}
</style>
