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
          <v-btn
            color="success"
            @click="goToCreate()"
          >
            Go to task creator
          </v-btn>
        </v-layout>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>

<script>
export default {
  name: 'TaskTemplateChooser',

  props: {
    showModal: Boolean
  },

  data () {
    return {
      chosenTemplate: '',
      possibleTemplates: [
        'No template',
        'TensorFlow 1.x',
        'TensorFlow 2.x',
        'PyTorch'
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

    setChosenTemplate: function (templateName) {
      switch (templateName) {
        case 'TensorFlow 1.x':
          this.chosenTemplate = 'tf1'
          break
        case 'TensorFlow 2.x':
          this.chosenTemplate = 'tf2'
          break
        case 'PyTorch':
          this.chosenTemplate = 'torch'
          break
        default: this.chosenTemplate = ''
      }
    },

    goToCreate: function () {
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
