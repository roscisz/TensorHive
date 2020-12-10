<template>
  <v-container>
    <v-layout class="mb-4">
      <v-flex xs12>
        <JobDetails
          :job="job"
          :loading="loadingJob"
          :performing-crud-action="performingJobCrudAction"
          @crud-action="performJobCrudAction"
        />
      </v-flex>
    </v-layout>

    <v-layout>
      <v-flex xs12>
        <TasksTable
          header="Job tasks"
          :elevation="1"
          :loading="loadingTasks"
          :performing-bulk-action="performingTaskBulkAction"
          :performing-crud-action="performingTaskCrudAction"
          :tasks="tasks"
          @add="addTask"
          @bulk-action="performTaskBulkAction"
          @crud-action="performTaskCrudAction"
        />
      </v-flex>
    </v-layout>

    <v-snackbar v-model="snackbar" bottom color="error">
      {{ errorMessage }}
      <v-btn flat @click="snackbar = false">Close</v-btn>
    </v-snackbar>
  </v-container>
</template>

<script>
import {
  getJob,
  executeJob,
  stopJob,
  killJob,
  deleteJob,
  createJobTask
} from '../../../api/jobs'
import { getTasks, deleteTask, updateTask } from '../../../api/tasks'
import { getErrorMessage } from '../../../utils/errors'
import { JobCrudActions } from './JobCrudActions'
import JobDetails from './JobDetails'
import { TaskBulkActions } from '../tasks_overview/TaskBulkActions'
import { TaskCrudActions } from '../tasks_overview/TaskCrudActions'
import TasksTable from '../tasks_overview/TasksTable'

export default {
  components: {
    JobDetails,
    TasksTable
  },
  data () {
    return {
      job: undefined,
      tasks: [],
      tasksMap: new Map(),
      loadingJob: true,
      loadingTasks: true,
      performingJobCrudAction: false,
      performingTaskBulkAction: false,
      performingTaskCrudAction: [],
      snackbar: false,
      errorMessage: '',
      headers: [
        { text: 'Name', name: 'name' },
        { text: 'Hostname', name: 'hostname' },
        { text: 'Command', name: 'command' },
        { text: 'Status', name: 'status' }
      ]
    }
  },
  watch: {
    $route: 'getJob'
  },
  mounted () {
    this.getJob()
  },
  methods: {
    getJob () {
      const id = this.$route.params.id
      this.loadingJob = true
      this.loadingTasks = true

      return Promise.all([
        getJob(this.$store.state.accessToken, id),
        getTasks(this.$store.state.accessToken, id)
      ])
        .then(([job, tasks]) => {
          this.job = job
          this.tasks = tasks
          this.tasksMap = this.createTasksMap(tasks)
          this.loadingJob = false
          this.loadingTasks = false
        })
        .catch(error => {
          this.handleError(error)
          this.loadingJob = false
          this.loadingTasks = false
        })
    },
    addTask (task) {
      this.loadingTasks = true

      createJobTask(this.$store.state.accessToken, this.job.id, task)
        .then(task => {
          this.tasksMap.set(task.id, task)
          this.syncTasks()

          this.loadingTasks = false
        })
        .catch(error => {
          this.handleError(error)

          this.loadingTasks = false
        })
    },
    editTask (task) {
      const { id, ...rest } = task

      return updateTask(this.$store.state.accessToken, id, rest)
    },
    performJobCrudAction (job, action) {
      let promise = null
      this.performingJobCrudAction = true
      this.loadingTasks = true

      switch (action) {
        case JobCrudActions.Execute:
          promise = this.executeJob(job)
          break
        case JobCrudActions.Stop:
          promise = this.stopJob(job)
          break
        case JobCrudActions.Kill:
          promise = this.killJob(job)
          break
        case JobCrudActions.Delete:
          promise = this.deleteJob(job)
          break
        default:
          this.performingJobCrudAction = false
          this.loadingTasks = false
          this.handleError(new Error(`Unknown action ${action}`))
      }

      if (promise) {
        if (action === JobCrudActions.Delete) {
          promise.then(() => this.$router.push('/jobs_overview'))
        } else {
          promise.then(([job, tasks]) => {
            this.job = job
            this.tasks = tasks
            this.tasksMap = this.createTasksMap(tasks)
            this.performingJobCrudAction = false
            this.loadingTasks = false
          })
        }

        promise.catch(error => {
          this.handleError(error)

          this.performingJobAction = false
          this.loadingTasks = false
        })
      }
    },
    performTaskBulkAction (tasks, action) {
      this.performingTaskBulkAction = true
      this.loadingTasks = true

      this.performTasksAction(tasks, action)
        .then(() => {
          this.performingTaskBulkAction = false
          this.loadingTasks = false
        })
        .catch(error => {
          this.handleError(error)

          this.performingTaskBulkAction = false
          this.loadingTasks = false
        })
    },
    performTaskCrudAction (task, action) {
      console.log(task, action)
      const index = this.performingTaskCrudAction.push(task.id) - 1
      this.loadingTasks = true

      this.performTasksAction([task], action)
        .then(() => {
          this.performingTaskCrudAction.splice(index, 1)
          this.loadingTasks = false
        })
        .catch(error => {
          this.handleError(error)
          this.performingTaskCrudAction.splice(index, 1)
          this.loadingTasks = false
        })
    },
    performTasksAction (tasks, action) {
      let promise = null

      switch (action) {
        case TaskCrudActions.Edit:
          promise = this.editTask(tasks[0]).then(task => [task])
          break
        case TaskCrudActions.Execute:
        case TaskBulkActions.Execute:
          promise = this.executeTasks(tasks)
          break
        case TaskCrudActions.Stop:
        case TaskBulkActions.Stop:
          promise = this.stopTasks(tasks)
          break
        case TaskCrudActions.Kill:
        case TaskBulkActions.Kill:
          promise = this.killTasks(tasks)
          break
        case TaskBulkActions.Copy:
          promise = this.copyTasks(tasks)
          break
        case TaskCrudActions.Delete:
        case TaskBulkActions.Delete:
          promise = this.deleteTasks(tasks)
          break
        default:
          promise = Promise.reject(new Error(`Unknown action '${action}'`))
      }

      return promise.then(tasks => {
        if (
          action === TaskCrudActions.Delete ||
          action === TaskBulkActions.Delete
        ) {
          for (const task of tasks) {
            this.taskMap.delete(task.id)
          }
        } else {
          for (const task of tasks) {
            this.taskMap.set(task.id, task)
          }
        }

        this.syncTasks()
      })
    },
    executeJob (job) {
      return executeJob(this.$store.state.accessToken, job.id).then(job =>
        getTasks(this.$store.state.accessToken, job.id).then(tasks => [
          job,
          tasks
        ])
      )
    },
    executeTasks (tasks) {
      // TODO: Do we add it?
    },
    stopJob (job) {
      return stopJob(this.$store.state.accessToken, job.id).then(job =>
        getTasks(this.$store.state.accessToken, job.id).then(tasks => [
          job,
          tasks
        ])
      )
    },
    stopTasks (tasks) {
      // TODO: Do we add it?
    },
    killJob (job) {
      return killJob(this.$store.state.accessToken, job.id).then(job =>
        getTasks(this.$store.state.accessToken, job.id).then(tasks => [
          job,
          tasks
        ])
      )
    },
    killTasks (tasks) {
      // TODO: Do we add it?
    },
    deleteJob (job) {
      return deleteJob(this.$store.state.accessToken, job.id)
    },
    deleteTasks (tasks) {
      return Promise.all(
        tasks.map(({ id }) => deleteTask(this.$store.state.accessToken, id))
      ).then(() => tasks)
    },
    createTasksMap (tasks) {
      return new Map(tasks.map(task => [task.id, task]))
    },
    syncTasks () {
      this.tasks = [...this.tasksMap.values()]
    },
    handleError (error) {
      this.errorMessage = getErrorMessage(error)
      this.snackbar = true
    }
  }
}
</script>

<style></style>
