<template>
  <v-container>
    <v-card outlined>
      <div
        class="editIcon"
        v-if="readOnly"
      >
        <v-layout>
          <v-flex xs12>
            <JobCrudActions
              :job-id="jobId"
              :performing-action="performingCrudAction"
              :show-details-action="false"
              @action="$emit('crud-action', job, $event)"
            />
          </v-flex>
        </v-layout>
      </div>
      <v-tabs v-model="activeTab">
        <v-tab :key="0">Job details</v-tab>
        <v-tab :key="1">Job tasks</v-tab>
        <v-tab-item key="info">
          <v-card flat>
            <v-card-text>
              <v-layout>
                <v-flex xs12>
                  <JobInfo
                    :readOnly="readOnly"
                    :job="job"
                    :loading="loadingJob"
                    :performing-crud-action="performingJobCrudAction"
                    @changeJob="changeJob"
                    @crud-action="performJobCrudAction"
                  />
                </v-flex>
              </v-layout>
            </v-card-text>
          </v-card>
        </v-tab-item>
        <v-tab-item key="timer">
          <v-card flat>
            <v-card-text>
              <v-layout>
                <v-flex xs12>
                  <JobTasks
                    header="Job tasks"
                    :elevation="1"
                    :loading="loadingTasks"
                    :tasks="tasks"
                    :existing-tasks="existingTasks"
                    :prototypes="prototypes"
                    :prototypingMode="!readOnly"
                    @updatePrototypes="updatePrototypes"
                    @updateTasks="updateTasks"
                    @removeTasks="removeTasks"
                  />
                </v-flex>
              </v-layout>
            </v-card-text>
          </v-card>
        </v-tab-item>
      </v-tabs>
      <v-card-actions>
        <v-layout align-center justify-end>
          <v-btn
            outlined
            rounded
            text
            @click="cancelHandler"
          >
            Cancel
          </v-btn>
          <v-btn
            v-if="!readOnly && activeTab===1"
            color="primary"
            outlined
            rounded
            :disabled="!job || job.name === ''"
            @click="saveHandler"
          >
            Save job
          </v-btn>
          <v-btn
            v-if="activeTab===0"
            color="primary"
            outlined
            rounded
            :disabled="!job || job.name === ''"
            @click="activeTab = 1"
          >
            Next step
          </v-btn>
        </v-layout>
      </v-card-actions>
    </v-card>
    <v-snackbar v-model="snackbar" bottom color="error">
        {{ errorMessage }}
        <v-btn flat @click="snackbar = false">Close</v-btn>
      </v-snackbar>
  </v-container>
</template>

<script>
import {
  getJob,
  createJobTask,
  createJob,
  updateJob
} from '../../../api/jobs'
import { getErrorMessage } from '../../../utils/errors'
import { getTasks, updateTask, deleteTask } from '../../../api/tasks'

import JobInfo from './job_steps/JobInfo'
import JobTasks from './JobTasks'
import JobCrudActions from './JobCrudActions'

export default {
  components: {
    JobInfo,
    JobTasks,
    JobCrudActions
  },
  data () {
    return {
      job: undefined,
      readOnly: true,
      tasks: [],
      tasksToRemove: [],
      tasksToUpdate: [],
      existingTasks: [],
      prototypes: [],
      loadingJob: false,
      loadingTasks: false,
      submitting: false,
      snackbar: false,
      errorMessage: '',
      activeTab: 0
    }
  },
  mounted () {
    this.viewInit()
  },
  watch: {
    $route (to, from) {
      this.viewInit()
    }
  },
  computed: {
    jobId () {
      return this.$route.params.id
    }
  },
  methods: {
    viewInit () {
      if (this.$route.fullPath.includes('/add') || this.$route.fullPath.includes('/edit')) {
        this.readOnly = false
      } else {
        this.readOnly = true
      }
      if (!this.$route.fullPath.includes('/add')) {
        this.getJob()
      }
      this.getAllTasks()
    },
    getJob () {
      this.loadingJob = true
      getJob(this.$store.state.accessToken, this.$route.params.id)
        .then((job) => {
          this.job = job
          this.loadingJob = false
        })
        .catch((error) => {
          this.errorHandler(error)
          this.loadingJob = false
        })

      this.loadingTasks = true
      getTasks(this.$store.state.accessToken, this.$route.params.id)
        .then((tasks) => {
          this.tasks = tasks
          this.originalTasks = tasks
          this.loadingTasks = false
        })
        .catch((error) => {
          this.errorHandler(error)
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
          .then(({ id }) => this.tasksHandler(id))
          .then(() => {
            this.submitting = false
            this.$router.push('/jobs_overview')
          })
          .catch(error => {
            this.submitting = false

            this.errorHandler(error)
          })
      } else {
        this.updateJob()
          .then(({ id }) => this.tasksHandler(id))
          .then(() => {
            this.submitting = false
            this.$router.push('/jobs_overview')
          })
          .catch(error => {
            this.submitting = false
            this.errorHandler(error)
          })
      }
    },
    editHandler () {
      this.$router.push(this.$route.fullPath + '/edit')
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
    tasksHandler (jobId) {
      return Promise.all(
        [...this.prototypes].map(({ hostname, command, cmdsegments }) =>
          createJobTask(this.$store.state.accessToken, jobId, {
            jobId,
            hostname,
            command,
            cmdsegments
          })
        ),
        [...this.tasksToUpdate].map((task) =>
          updateTask(this.$store.state.accessToken, task.id, task)
        ),
        [...this.tasksToRemove].map((task) =>
          deleteTask(this.$store.state.accessToken, task.id)
        )
      )
    },
    updateJob () {
      // const { description, name, startAt, stopAt } = this.job
      const { description, name } = this.job
      return updateJob(this.$store.state.accessToken, this.$route.params.id, {
        name,
        description: description || ''
        // userId: this.$store.state.id,
        // startAt: (startAt && startAt.toISOString()) || null,
        // stopAt: (stopAt && stopAt.toISOString()) || null
      })
    },
    updatePrototypes (prototypes) {
      this.prototypes = prototypes
    },
    updateTasks (tasks) {
      this.tasksToUpdate = tasks
    },
    removeTasks (tasks) {
      this.tasksToRemove = tasks
    },
    cancelHandler () {
      if (this.$route.fullPath.includes('/add') || this.readOnly === true) {
        this.$router.push('/jobs_overview')
      } else {
        this.$router.push(this.$route.fullPath.replace('/edit', ''))
      }
    },
    errorHandler (error) {
      this.errorMessage = getErrorMessage(error)
      this.snackbar = true
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
