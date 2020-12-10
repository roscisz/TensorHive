<template>
  <div>
    <v-container>
      <v-layout>
        <v-flex xs12>
          <v-stepper v-model="step">
            <v-stepper-header>
              <v-stepper-step step="1" :complete="step > 1">
                Job Information
              </v-stepper-step>
              <v-divider></v-divider>
              <v-stepper-step step="2" :complete="step > 2">
                Job Tasks
              </v-stepper-step>
            </v-stepper-header>

            <v-stepper-items>
              <v-stepper-content step="1">
                <JobBasicInfoStep
                  :backButton="false"
                  @continue="finishFirstStep"
                />
              </v-stepper-content>

              <v-stepper-content step="2">
                <JobTasksStep
                  continue-button-text="Submit"
                  :continue-button-loading="submitting"
                  @back="step = 1"
                  @continue="finishSecondStep"
                  @error="handleError"
                />
              </v-stepper-content>
            </v-stepper-items>
          </v-stepper>
        </v-flex>
      </v-layout>
    </v-container>

    <v-snackbar v-model="snackbar" bottom color="error">
      {{ errorMessage }}
      <v-btn flat @click="snackbar = false">Close</v-btn>
    </v-snackbar>
  </div>
</template>

<script>
import { createJob, createJobTask } from '../../../api/jobs'
import { getErrorMessage } from '../../../utils/errors'
import JobBasicInfoStep from './job_steps/JobBasicInfoStep'
import JobTasksStep from './job_steps/JobTasksStep'

export default {
  components: { JobBasicInfoStep, JobTasksStep },
  data () {
    return {
      step: 1,
      job: undefined,
      selectedTasks: [],
      newTasks: [],
      submitting: false,
      snackbar: false,
      errorMessage: ''
    }
  },
  methods: {
    finishFirstStep (job) {
      this.job = job
      this.step = 2
    },
    finishSecondStep (selectedTasks, newTasks) {
      this.selectedTasks = selectedTasks
      this.newTasks = newTasks

      this.finish()
    },
    finish () {
      this.submitting = true

      this.createJob()
        .then(({ id }) => this.createTasks(id))
        .then(() => {
          this.submitting = false
          this.step = 3

          this.$router.push('/jobs_overview')
        })
        .catch(error => {
          this.submitting = false

          this.handleError(error)
        })
    },
    handleError (error) {
      this.errorMessage = getErrorMessage(error)
      this.snackbar = true
    },
    createJob () {
      const { description, name, startAt, stopAt } = this.job

      return createJob(this.$store.state.accessToken, {
        name,
        description: description || '',
        userId: this.$store.state.id,
        startAt: (startAt && startAt.toISOString()) || null,
        stopAt: (stopAt && stopAt.toISOString()) || null
      })
    },
    createTasks (jobId) {
      return Promise.all(
        [...this.selectedTasks, ...this.newTasks].map(({ hostname, command }) =>
          createJobTask(this.$store.state.accessToken, jobId, {
            jobId,
            hostname,
            command
          })
        )
      )
    }
  }
}
</script>

<style scoped>
/* This resets font weight set by Bootstrap to the default 'normal' value. */
/* The proper way of creating a deep selector would be using `::v-deep` but */
/* it requires Vue Loader v15 which we do not use for now. */
>>> label {
  font-weight: normal;
}
</style>
