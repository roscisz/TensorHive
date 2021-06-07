<template>
  <v-flex xs12 sm6 md8 v-if="!editMode">
    <JobDetailsField v-slot="props" header="Description" :value="description">
      <div class="description">{{ props.value }}</div>
    </JobDetailsField>
  </v-flex>
  <v-flex xs12 v-else>
    <v-textarea
      :value="description"
      @change="changeDescription"
      auto-grow
      box
      label="Description"
      rows="4"
    ></v-textarea>
  </v-flex>
</template>

<script>
import JobDetailsField from './JobDetailsField'

export default {
  components: { JobDetailsField },
  props: {
    editMode: Boolean,
    description: String
  },
  methods: {
    changeDescription (value) {
      this.$emit('changeDescription', value)
    }
  }
}
</script>

<style scoped>
  .description {
    max-height: 280px;
    overflow-y: auto;
    white-space: pre-line;
  }
</style>
