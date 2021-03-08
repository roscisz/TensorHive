<template>
  <TaskForm
    header="Edit the task"
    :hostname="task.hostname"
    :resource="parsedCommand.resource"
    :command="parsedCommand.command"
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
    parsedCommand () {
      let command = this.task.command
      const match = /CUDA_VISIBLE_DEVICES=(\d*)/.exec(command)

      if (match && match[1]) {
        return {
          resource: { name: `GPU${match[1]}`, id: Number(match[1]) },
          command: command.replace(/CUDA_VISIBLE_DEVICES=(\d*) /, '')
        }
      }

      return {
        resource: { name: 'CPU', id: null },
        command: command.replace('CUDA_VISIBLE_DEVICES=', '')
      }
    }
  },
  methods: {
    editTask (task) {
      this.$emit('edit', { ...task, id: this.task.id })
    }
  }
}
</script>
