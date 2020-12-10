<template>
  <v-form ref="form" v-model="valid">
    <v-container grid-list-md>
      <v-layout wrap>
        <v-flex xs12 sm6>
          <v-select
            v-model="internalHostname"
            box
            required
            label="Hostname*"
            :items="hostnames"
            :rules="hostnameRules"
            @input="$emit('update:hostname', $event)"
          ></v-select>
        </v-flex>

        <v-flex xs12 sm6>
          <v-select
            v-model="internalResource"
            box
            required
            return-object
            item-text="name"
            item-value="id"
            label="Resource*"
            :items="resources"
            :rules="resourceRules"
            @input="$emit('update:resource', $event)"
          ></v-select>
        </v-flex>

        <v-flex xs12>
          <v-textarea
            class="text-monospace"
            v-model="internalCommand"
            auto-grow
            box
            required
            label="Command*"
            rows="2"
            :counter="commandCounter"
            :rules="commandRules"
            @input="$emit('update:command', $event)"
          ></v-textarea>
        </v-flex>
      </v-layout>
    </v-container>
  </v-form>
</template>

<script>
import { required, maxLength } from '../../../../utils/rules'

const commandCounter = 400

export default {
  props: {
    hosts: {
      type: Object,
      required: true
    },
    hostname: String,
    resource: Object,
    command: String
  },
  data () {
    return {
      valid: false,
      internalHostname: this.hostname,
      internalResource: this.resource,
      internalCommand: this.command,
      commandCounter,
      hostnameRules: [required('hostname')],
      resourceRules: [required('resource')],
      commandRules: [
        required('command'),
        maxLength('command', commandCounter)
      ]
    }
  },
  computed: {
    hostnames () {
      return Object.keys(this.hosts)
    },
    resources () {
      return this.hostname ? this.hosts[this.hostname] : []
    }
  },
  methods: {
    reset () {
      this.$refs.form.reset()
    },
    validate () {
      return this.$refs.form.validate()
    }
  }
}
</script>

<style scoped>
.text-monospace >>> textarea {
  font-family: ui-monospace, "SF Mono", SFMono-Regular, "DejaVu Sans Mono",
    Liberation Mono, Menlo, Consolas, Monaco, monospace;
}
</style>
