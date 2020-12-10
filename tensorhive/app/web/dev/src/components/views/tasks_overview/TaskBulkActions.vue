<template>
  <v-layout>
    <v-select
      v-model="action"
      solo
      hide-details
      color="primary"
      label="Action"
      :items="actions"
    ></v-select>
    <v-btn
      color="primary"
      :loading="performingAction"
      :small="smallPerformButton"
      @click="$emit('action', action)"
    >
      Perform
    </v-btn>
  </v-layout>
</template>

<script>
export const TaskBulkActions = {
  Execute: 'Execute',
  Stop: 'Stop',
  Kill: 'Kill',
  Copy: 'Copy',
  Delete: 'Delete'
}

export default {
  props: {
    performingAction: {
      type: Boolean,
      default: false
    },
    smallPerformButton: {
      type: Boolean,
      default: false
    }
  },
  data () {
    return {
      action: undefined,
      actions: Object.values(TaskBulkActions)
    }
  }
}
</script>
