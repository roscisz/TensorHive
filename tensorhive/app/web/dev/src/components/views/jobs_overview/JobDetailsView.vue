<template>
  <v-container>
    <h5 class="headline mx-2">Job info</h5>
    <v-spacer></v-spacer>
    <v-card outlined :loading="loadingJob">
      <div class="editIcon" v-if="!editMode">
        <v-layout>
          <v-flex xs12>
            <JobCrudActions
              :job-id="jobId"
              :performing-action="performingJobCrudAction"
              :show-details-action="false"
              @action="performJobCrudAction"
            />
          </v-flex>
        </v-layout>
      </div>
      <v-card-text>
        <v-layout>
          <v-flex xs12>
            <JobInfo
              :editMode="editMode"
              :job="job"
              :loading="loadingJob"
              @changeJob="changeJob"
            />
          </v-flex>
        </v-layout>
      </v-card-text>
      <v-card-actions>
        <v-layout align-center justify-end>
          <v-btn outlined rounded text @click="cancelHandler">Cancel</v-btn>
          <v-btn
            v-if="editMode"
            color="primary"
            outlined
            rounded
            :disabled="!job || job.name === ''"
            @click="saveHandler"
          >Save job</v-btn>
        </v-layout>
      </v-card-actions>
    </v-card>

    <h5 class="headline mx-2 mt-4" v-if="jobId">Job tasks</h5>
    <v-spacer v-if="jobId"></v-spacer>
    <v-card outlined :loading="loadingTasks" v-if="jobId">
      <v-card-text>
        <v-layout>
          <v-flex xs12>
            <JobTasks
              header="Job tasks"
              :elevation="1"
              :loading="loadingTasks"
              :tasks="tasks"
              :existing-tasks="existingTasks"
              :editMode="editMode"
              @addTasks="addTasks"
              @updateTasks="updateTasks"
              @removeTasks="removeTasks"
              @error="errorHandler"
            />
          </v-flex>
        </v-layout>
      </v-card-text>
    </v-card>
    <v-snackbar v-model="snackbar" bottom color="error">
      {{ errorMessage }}
      <v-btn flat @click="snackbar = false">Close</v-btn>
    </v-snackbar>
  </v-container>
</template>

<script>
import moment from 'moment'
import {
  getJob,
  createJobTask,
  createJob,
  updateJob,
  executeJob,
  stopJob,
  killJob,
  deleteJob
} from '../../../api/jobs'
import { getErrorMessage } from '../../../utils/errors'
import { getTasks, updateTask, deleteTask } from '../../../api/tasks'

import JobInfo from './job_details_view/JobInfo'
import JobTasks from './job_details_view/JobTasks'
import JobCrudActions, { Actions } from './JobCrudActions'

export default {
  components: {
    JobInfo,
    JobTasks,
    JobCrudActions
  },
  data () {
    return {
      job: undefined,
      editMode: false,
      tasks: [],
      existingTasks: [],
      loadingJob: false,
      loadingTasks: false,
      performingJobCrudAction: false,
      submitting: false,
      snackbar: false,
      errorMessage: '',
      activeTab: 0,
      interval: null
    }
  },
  mounted () {
    this.viewInit()
    let self = this
    this.interval = setInterval(() => {
      if (!self.$route.fullPath.includes('/job/')) {
        clearInterval(self.interval)
      } else {
        self.viewInit()
      }
    }, 10000)
  },
  watch: {
    $route (to, from) {
      this.viewInit()
    }
  },
  computed: {
    jobId () {
      return +this.$route.params.id
    }
  },
  methods: {
    viewInit () {
      if (this.$route.fullPath.includes('/add') || this.$route.fullPath.includes('/edit')) {
        this.editMode = true
      } else {
        this.editMode = false
      }
      if (!this.$route.fullPath.includes('/add')) {
        this.getJob()
        this.getTasks()
      }
    },
    getJob () {
      this.loadingJob = true
      getJob(this.$store.state.accessToken, this.$route.params.id)
        .then((job) => {
          this.job = job
        })
        .catch((error) => {
          this.errorHandler(error)
        })
        .finally(() => {
          this.loadingJob = false
        })
    },
    getTasks () {
      this.loadingTasks = true
      getTasks(this.$store.state.accessToken, this.$route.params.id)
        .then((tasks) => {
          this.tasks = tasks
        })
        .catch((error) => {
          this.errorHandler(error)
        })
        .finally(() => {
          this.loadingTasks = false
        })
    },
    changeJob (job) {
      this.job = job
    },
    saveHandler () {
      this.submitting = true
      if (this.$route.fullPath.includes('/add')) {
        this.createJob()
          .then(({ id }) => {
            this.submitting = false
            this.$router.push('/job/' + id + '/edit')
          })
          .catch(error => {
            this.submitting = false

            this.errorHandler(error)
          })
      } else {
        this.updateJob()
          .then(() => {
            this.submitting = false
            this.$router.push('/job/' + this.jobId)
          })
          .catch(error => {
            this.submitting = false
            this.errorHandler(error)
          })
      }
    },
    createJob () {
      const { description, name, startAt, stopAt } = this.job

      return createJob(this.$store.state.accessToken, {
        name,
        description: description || '',
        userId: this.$store.state.id,
        startAt: !startAt ? null : startAt,
        stopAt: !stopAt ? null : stopAt
      })
    },
    addTasks (tasksToAdd) {
      this.loadingTasks = true
      Promise.all(
        tasksToAdd.map(({ hostname, command, cmdsegments }) =>
          createJobTask(this.$store.state.accessToken, this.jobId, {
            jobId: this.jobId,
            hostname,
            command,
            cmdsegments
          }))
      ).then(() => {
        this.getTasks()
      }).catch(error => {
        this.loadingTasks = false
        this.errorHandler(error)
      })
    },
    updateTasks (tasksToUpdate) {
      this.loadingTasks = true
      Promise.all(
        tasksToUpdate.map((task) =>
          updateTask(this.$store.state.accessToken, task.id, task)
        )
      ).then(() => {
        this.getTasks()
      }).catch(error => {
        this.loadingTasks = false
        this.errorHandler(error)
      })
    },
    removeTasks (tasksToRemove) {
      this.loadingTasks = true
      return Promise.all(
        tasksToRemove.map((task) =>
          deleteTask(this.$store.state.accessToken, task.id)
        )
      ).then(() => {
        this.getTasks()
      }).catch(error => {
        this.loadingTasks = false
        this.errorHandler(error)
      })
    },
    updateJob () {
      const { description, name, startAt, stopAt } = this.job

      return updateJob(this.$store.state.accessToken, this.$route.params.id, {
        name,
        description: description || '',
        startAt: !startAt ? null : moment(startAt).toISOString(),
        stopAt: !stopAt ? null : moment(stopAt).toISOString()
      })
    },
    cancelHandler () {
      if (this.$route.fullPath.includes('/add') || this.editMode === false) {
        this.$router.push('/jobs_overview')
      } else {
        this.$router.push(this.$route.fullPath.replace('/edit', ''))
      }
    },
    errorHandler (error) {
      this.errorMessage = getErrorMessage(error)
      this.snackbar = true
    },
    performJobCrudAction (action) {
      let promise = null
      this.performingJobCrudAction = true
      this.loadingTasks = true

      switch (action) {
        case Actions.Execute:
          promise = this.executeJob()
          break
        case Actions.Stop:
          promise = this.stopJob()
          break
        case Actions.Kill:
          promise = this.killJob()
          break
        case Actions.Delete:
          promise = this.deleteJob()
          break
        default:
          this.performingJobCrudAction = false
          this.loadingTasks = false
          this.handleError(new Error(`Unknown action ${action}`))
      }

      if (promise) {
        if (action === Actions.Delete) {
          promise.then(() => this.$router.push('/jobs_overview'))
        } else {
          promise.then(([job, tasks]) => {
            this.job = job
            this.tasks = tasks
            this.performingJobCrudAction = false
            this.loadingTasks = false
          })
        }

        promise.catch(error => {
          this.errorHandler(error)
          this.performingJobCrudAction = false
          this.loadingTasks = false
        })
      }
    },
    executeJob () {
      return executeJob(this.$store.state.accessToken, this.job.id).then(job =>
        getTasks(this.$store.state.accessToken, this.job.id).then(tasks => [
          job,
          tasks
        ])
      )
    },
    stopJob () {
      return stopJob(this.$store.state.accessToken, this.job.id).then(job =>
        getTasks(this.$store.state.accessToken, this.job.id).then(tasks => [
          job,
          tasks
        ])
      )
    },
    killJob () {
      return killJob(this.$store.state.accessToken, this.job.id).then(job =>
        getTasks(this.$store.state.accessToken, this.job.id).then(tasks => [
          job,
          tasks
        ])
      )
    },
    deleteJob () {
      return deleteJob(this.$store.state.accessToken, this.job.id)
    }
  }
}
</script>

<style>
  .editIcon {
    position: absolute;
    right: 12px;
    top: 12px;
    z-index: 9999;
  }
</style>
