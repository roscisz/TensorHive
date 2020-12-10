<template>
  <TaskForm
    header="Edit the task"
    :hostname="task.hostname"
    :resource="resource"
    :command="task.command"
    @cancel="$emit('cancel', $event)"
    @submit="editTask"
  />
</template>

<script>
import TaskForm from './TaskForm/TaskForm'

export default {
  components: { TaskForm },
  props: {
    task: {
      type: Object,
      required: true
    }
  },
  computed: {
    // We should change the Task model in the future to simplify these
    // operations.
    resource () {
      const match = /CUDA_VISIBLE_DEVICES=(\d*)/.exec(this.task.command)

      if (match && match[1]) {
        return { name: `GPU${match[1]}`, id: Number(match[1]) }
      }

      return { name: 'CPU', id: null }
    }
  },
  methods: {
    editTask (task) {
      this.$emit('edit', { ...task, id: this.task.id })
    }
  }
}
</script>
