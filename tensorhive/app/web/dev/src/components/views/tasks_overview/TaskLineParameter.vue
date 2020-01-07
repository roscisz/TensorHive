<template>
  <v-layout align-center justify-start>
    <v-text-field
      class="task-input"
      :label="newParameter"
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
    parameter: String,
    value: String
  },

  data () {
    return {
      newParameter: '',
      newValue: ''
    }
  },

  created () {
    this.newParameter = this.parameter
    this.newValue = this.value
  },

  watch: {
    value () {
      this.newValue = this.value
    },
    newParameter () {
      this.$emit('changeParameter', this.newParameter, this.newValue)
    },
    newValue () {
      this.$emit('changeParameter', this.newParameter, this.newValue)
    }
  },

  methods: {
    removeMe: function () {
      this.$emit('deleteParameter')
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
