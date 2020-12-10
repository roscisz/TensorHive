<template>
  <div>
    <v-subheader>{{ header }}</v-subheader>
    <div class="px-3">
      <slot v-if="isSpecified" v-bind:value="value">{{ fieldValue }}</slot>
      <span v-else>{{ notSpecifiedText }}</span>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    header: {
      type: String,
      required: true
    },
    notSpecifiedText: {
      type: String,
      default: 'Not specified'
    },
    notSpecifiedValues: {
      type: Array,
      default () {
        return [undefined, null, '']
      }
    },
    value: {}
  },
  computed: {
    isSpecified () {
      return this.notSpecifiedValues.every(value => value !== this.value)
    },
    fieldValue () {
      return String(this.value)
    }
  }
}
</script>
