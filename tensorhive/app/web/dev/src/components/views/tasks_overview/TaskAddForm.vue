<template>
  <TaskForm
    header="Add a new task"
    @cancel="$emit('cancel', $event)"
    @submit="addTask"
    :chosen-template="chosenTemplate"
  />
</template>

<script>
import TaskForm from './TaskForm/TaskForm'

export default {
  components: { TaskForm },
  props: { chosenTemplate: String },
  methods: {
    addTask (task) {
      this.$emit('add', { ...task, status: 'prototype' })
    }
  }
}
</script>
