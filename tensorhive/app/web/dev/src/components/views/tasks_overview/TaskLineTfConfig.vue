<template>
  <v-layout align-center justify-start>
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
</template>

<script>
import TfConfigEdit from './TfConfigEdit'
export default {
  components: {TfConfigEdit},

  name: 'TaskLineTfConfig',

  props: {
    value: String
  },

  data () {
    return {
      newValue: '',
      showModalTfConfigEdit: false
    }
  },

  created () {
    this.newValue = this.value
  },

  watch: {
    value () {
      this.newValue = this.value
    },
    newValue () {
      this.$emit('changeTfConfig', this.newValue)
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
</style>
