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
        <span class="headline">TF_CONFIG editor</span>
      </v-card-text>
      <v-card-text>
        <v-textarea
          solo
          auto-grow
          label="Enter TF_CONFIG JSON here"
          v-model="newValue"
        />
      </v-card-text>
      <v-card-text>
        <v-layout align-center justify-end>
          <v-tooltip :disabled="properJson" top color="red">
            <template v-slot:activator="{ on }">
              <div v-on="on">
                <v-btn
                  color="success"
                  @click="save()"
                  :disabled="!properJson"
                >
                  Save
                </v-btn>
              </div>
            </template>
            <span>TF_CONFIG needs to be proper JSON object</span>
          </v-tooltip>
        </v-layout>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>

<script>
export default {
  name: 'TfConfigEdit',

  props: {
    value: String,
    showModal: Boolean
  },

  data () {
    return {
      newValue: '',
      properJson: false,
      show: false
    }
  },

  watch: {
    showModal () {
      this.show = this.showModal
    },
    show () {
      if (this.show === false) this.close()
      else this.newValue = this.desanitize(this.value)
    },

    newValue () {
      try {
        JSON.parse(this.newValue)
        this.properJson = true
      } catch (e) {
        this.properJson = false
      }
    }
  },

  methods: {
    close: function () {
      this.$emit('close')
    },

    save: function () {
      this.close()
      this.$emit('updateValue', this.sanitize(this.newValue))
    },

    sanitize: function (value) {
      value = JSON.stringify(JSON.parse(value))
      return '\'' + value.split('"').join('\\"') + '\''
    },

    desanitize: function (value) {
      try {
        return JSON.stringify(JSON.parse(value.split('\'').join('').split('\\"').join('"')), null, 2)
      } catch (e) {
        return value
      }
    }
  }
}
</script>

<style scoped>
  .float-right-button {
    float: right;
  }
</style>
