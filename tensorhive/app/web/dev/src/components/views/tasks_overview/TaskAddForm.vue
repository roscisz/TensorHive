<template>
  <TaskForm
    header="Add a new task"
    @cancel="$emit('cancel', $event)"
    @submit="addTask"
  />
</template>

<script>
import TaskForm from './TaskForm/TaskForm'

export default {
  components: { TaskForm },
  methods: {
    addTask (task) {
      this.$emit('add', { ...task, status: 'prototype' })
    }
  }
}
</script>
