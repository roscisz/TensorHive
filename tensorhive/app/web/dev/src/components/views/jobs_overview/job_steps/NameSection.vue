<template>
  <v-flex xs12 sm6 md4 v-if="readOnly">
    <JobDetailsField header="Name" :value="name" />
  </v-flex>
  <v-flex xs12 v-else>
    <v-text-field
      :value="name"
      @change="changeName"
      box
      persistent-hint
      required
      hint="*Required"
      label="Name*"
      :counter="nameCounter"
      :rules="nameRules"
    ></v-text-field>
  </v-flex>
</template>

<script>
import JobDetailsField from '../JobDetailsField'
import { required, maxLength } from '../../../../utils/rules'

const nameCounter = 40

export default {
  components: { JobDetailsField },
  props: {
    readOnly: Boolean,
    name: String
  },
  data () {
    return {
      nameCounter,
      nameRules: [required('name'), maxLength('name', nameCounter)]
    }
  },
  methods: {
    changeName (value) {
      this.$emit('changeName', value)
    }
  }
}
</script>
