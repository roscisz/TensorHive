<template>
  <v-form ref="form" v-model="valid">
    <v-container grid-list-md>
      <v-layout wrap>
        <v-flex xs12 sm4>
          <v-select
            v-model="type"
            box
            required
            label="Type*"
            :items="types"
            :rules="typeRules"
          ></v-select>
        </v-flex>

        <v-flex xs12 sm4>
          <v-text-field
            v-model="name"
            box
            required
            label="Name*"
            :counter="nameCounter"
            :rules="nameRules"
          ></v-text-field>
        </v-flex>

        <v-flex xs12 sm4>
          <v-text-field
            v-model="value"
            box
            persistent-hint
            hint="Optional"
            label="Value"
          ></v-text-field>
        </v-flex>

        <v-flex class="text-xs-right" xs12>
          <v-btn class="mx-0" small color="primary" @click="add">Add</v-btn>
        </v-flex>
      </v-layout>
    </v-container>
  </v-form>
</template>

<script>
import { required, maxLength, startsWith } from '../../../../utils/rules'

const env = 'Environment variable'
const param = 'Parameter'
const nameCounter = 50

export default {
  data () {
    return {
      valid: false,
      type: undefined,
      name: undefined,
      nameCounter,
      value: undefined,
      types: [env, param],
      typeRules: [required('type')]
    }
  },
  computed: {
    nameRules () {
      const rules = [required('name'), maxLength('name', nameCounter)]

      if (this.type === param) {
        rules.push(startsWith('name', '-'))
      }

      return rules
    }
  },
  methods: {
    add () {
      if (this.validate()) {
        if (this.type === env) {
          this.$emit('addEnv', this.name, this.value)
        } else {
          this.$emit('addParam', this.name, this.value)
        }

        this.reset()
      }
    },
    reset () {
      this.$refs.form.reset()
    },
    validate () {
      return this.$refs.form.validate()
    }
  }
}
</script>
