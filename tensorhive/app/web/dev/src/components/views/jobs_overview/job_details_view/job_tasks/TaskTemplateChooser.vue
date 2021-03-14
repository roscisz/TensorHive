<template>
  <v-dialog width="80vw" v-model="showModal">
    <template v-slot:activator="{ on }">
      <v-btn
        v-on="on"
        color="primary"
        @click="$emit('open')"
      >Add Tasks From Template</v-btn>
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
        <span class="headline">Choose framework template</span>
      </v-card-text>
      <v-card-text>
        <v-select
          :items="possibleTemplates"
          label="Choose template from list"
          @change="setChosenTemplate"
          solo
        ></v-select>
      </v-card-text>
      <v-card-text>
        <v-layout align-center justify-end>
          <v-btn color="primary" @click="goToCreate()">Go to task creator</v-btn>
        </v-layout>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>

<script>
export default {
  name: 'TaskTemplateChooser',
  props: {
    showModal: {
      type: Boolean,
      default: false
    }
  },
  data () {
    return {
      chosenTemplate: '',
      possibleTemplates: [
        'No template',
        'TensorFlow - cluster parameters',
        'TensorFlow - TF_CONFIG',
        'PyTorch'
      ]
    }
  },

  methods: {
    close () {
      this.$emit('close')
    },

    setChosenTemplate (templateName) {
      switch (templateName) {
        case 'TensorFlow - cluster parameters':
          this.chosenTemplate = 'tf1'
          break
        case 'TensorFlow - TF_CONFIG':
          this.chosenTemplate = 'tf2'
          break
        case 'PyTorch':
          this.chosenTemplate = 'torch'
          break
        default: this.chosenTemplate = ''
      }
    },

    goToCreate () {
      this.close()
      this.$emit('openFromTemplate', this.chosenTemplate)
    }
  }
}
</script>

<style scoped>
  .float-right-button {
    float: right;
  }
</style>
