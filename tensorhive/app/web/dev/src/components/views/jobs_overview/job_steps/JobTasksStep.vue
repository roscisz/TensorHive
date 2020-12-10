<template>
  <div>
    <h5 class="headline">Add tasks to the job</h5>
    <v-container class="pa-3">
      <v-layout class="mb-5">
        <v-flex xs12>
          <TasksTable
            no-data-text="No existing tasks to display"
            :loading="loading"
            :prototypes.sync="newTasks"
            :prototyping-mode="true"
            :selected.sync="selected"
            :small-add-button="true"
            :tasks="tasks"
          />
        </v-flex>
      </v-layout>

      <v-layout>
        <v-btn
          v-if="backButton"
          flat
          color="primary"
          :loading="backButtonLoading"
          @click="$emit('back')"
        >
          {{ backButtonText }}
        </v-btn>
        <v-spacer></v-spacer>
        <v-btn
          v-if="continueButton"
          color="primary"
          :loading="continueButtonLoading"
          @click="$emit('continue', selected, newTasks)"
        >
          {{ continueButtonText }}
        </v-btn>
      </v-layout>
    </v-container>
  </div>
</template>

<script>
import { getTasks } from '../../../../api/tasks'
import TasksTable from '../../tasks_overview/TasksTable'

export default {
  components: { TasksTable },
  props: {
    backButton: {
      type: Boolean,
      default: true
    },
    backButtonText: {
      type: String,
      default: 'Back'
    },
    backButtonLoading: Boolean,
    continueButton: {
      type: Boolean,
      default: true
    },
    continueButtonText: {
      type: String,
      default: 'Continue'
    },
    continueButtonLoading: Boolean,
    selectedTasks: {
      type: Array,
      default () {
        return []
      }
    }
  },
  data () {
    return {
      loading: true,
      tasks: [],
      selected: this.selectedTasks,
      newTasks: []
    }
  },
  mounted () {
    getTasks(this.$store.state.accessToken)
      .then(tasks => {
        this.tasks = tasks
        this.loading = false
      })
      .catch(error => {
        this.loading = false

        this.$emit('error', error)
      })
  }
}
</script>
