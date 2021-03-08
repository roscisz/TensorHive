<template>
  <v-container class="pa-0">
    <v-layout class="mb-2" align-center>
      <v-layout class="px-4" v-if="prototypingMode" align-center>
        <v-icon>info</v-icon>
        <div class="ml-2 caption grey--text text--darken-1">
          Newly added tasks have the <i>Prototype</i> status and they will be
          saved along with this job.
        </div>
      </v-layout>
      <v-spacer></v-spacer>
      <v-tooltip v-if="showBulkActions" bottom>
        <template v-slot:activator="{ on }">
          <v-btn
            class="ma-0"
            v-on="on"
            flat
            icon
            small
            color="grey"
            :readonly="performingAction"
            @click="editMultipleTasks"
          >
            <v-icon small>edit</v-icon>
          </v-btn>
        </template>
        <span>Edit selected tasks</span>
      </v-tooltip>
      <v-tooltip v-if="showBulkActions" bottom>
        <template v-slot:activator="{ on }">
          <v-btn
            class="ma-0"
            v-on="on"
            flat
            icon
            small
            color="grey"
            :readonly="performingAction"
            @click="removeTasks"
          >
            <v-icon small>delete</v-icon>
          </v-btn>
        </template>
        <span>Remove selected tasks</span>
      </v-tooltip>
      <v-spacer></v-spacer>
      <TaskCreate
        v-if="prototypingMode"
        :show-modal="addMultipleDialog"
        :chosen-template="chosenTemplate"
        :selected-tasks="selectedTasks"
        :editing-tasks="editingTasks"
        @open="addMultipleDialog = true"
        @close="addMultipleDialog = false; chosenTemplate = ''; selectedTasks = []"
        @add="addPrototypes"
        @edit="editTasks"
      />
      <TaskTemplateChooser
        v-if="prototypingMode"
        :show-modal="templateDialog"
        @open="templateDialog = true"
        @close="templateDialog = false"
        @openFromTemplate="openFromTemplate"
      />
      <TaskDuplicate
        v-if="prototypingMode"
        :existing-tasks="existingTasks"
        :show-modal="duplicateDialog"
        @open="duplicateDialog = true"
        @close="duplicateDialog = false"
        @openFromExisting="openFromExisting"
      />
    </v-layout>
    <v-layout>
      <v-flex xs12>
        <v-data-table
          v-bind:class="`elevation-${elevation}`"
          v-model="internalSelected"
          item-key="id"
          :select-all="prototypingMode"
          :headers="headers"
          :items="tasks"
          :loading="loading"
          :no-data-text="noDataText"
          :pagination.sync="pagination"
          @input="$emit('update:selected', $event)"
        >
          <template v-slot:items="props">
            <tr>
              <td v-if="prototypingMode">
                <v-tooltip bottom>
                  <template v-slot:activator="{ on }">
                    <v-checkbox
                      v-on="on"
                      v-model="props.selected"
                      hide-details
                      color="primary"
                    ></v-checkbox>
                  </template>
                  <span v-if="!props.selected">Select to perform actions</span>
                  <span v-else>Task selected</span>
                </v-tooltip>
              </td>

              <td>{{ props.item.hostname }}</td>

              <td class="command-cell">
                <TaskCommand no-command-text="" :command="props.item.command" />
              </td>

              <td>
                <TaskStatus class="ma-0" :status="props.item.status" />
              </td>

              <td class="text-tabular-nums text-xs-right">
                {{ props.item.pid }}
              </td>

              <td>
                <TaskCrudActions
                  :read-only="!prototypingMode"
                  :performing-action="isPerformingCrud(props.item.id)"
                  :task="props.item"
                  @action="emitCrudAction"
                />
              </td>
            </tr>
          </template>

          <template v-if="prototypingMode" v-slot:footer>
            <tr v-for="task in internalPrototypes" :key="task.id">
              <td>
                <v-tooltip bottom>
                  <template v-slot:activator="{ on }">
                    <v-checkbox
                      v-on="on"
                      hide-details
                      readonly
                      color="grey"
                      on-icon="add"
                      :input-value="true"
                    ></v-checkbox>
                  </template>
                  <span>This task will be created</span>
                </v-tooltip>
              </td>

              <td>{{ task.hostname }}</td>

              <td class="command-cell">
                <TaskCommand no-command-text="" :command="task.command" />
              </td>

              <td>
                <TaskStatus class="ma-0" :status="task.status" />
              </td>

              <td><!-- Skipping. Prototypes do not have PID. --></td>

              <td>
                <v-layout align-center justify-end>
                  <v-tooltip bottom>
                    <template v-slot:activator="{ on }">
                      <v-btn
                        class="mr-0"
                        v-on="on"
                        flat
                        icon
                        color="grey"
                        @click="removePrototype(task.id)"
                      >
                        <v-icon>delete</v-icon>
                      </v-btn>
                    </template>
                    <span>Remove</span>
                  </v-tooltip>
                </v-layout>
              </td>
            </tr>
          </template>
        </v-data-table>
      </v-flex>
    </v-layout>
  </v-container>
</template>

<script>
// import api from '../../../api'
import TaskBulkActions from '../tasks_overview/TaskBulkActions'
import TaskCommand from '../tasks_overview/TaskCommand'
import TaskCrudActions from '../tasks_overview/TaskCrudActions'
import TaskStatus from '../tasks_overview/TaskStatus'
import TaskDuplicate from '../tasks_overview/TaskDuplicate'
import TaskTemplateChooser from '../tasks_overview/TaskTemplateChooser'
import TaskCreate from '../tasks_overview/TaskCreate'

export default {
  components: {
    TaskBulkActions,
    TaskCommand,
    TaskCrudActions,
    TaskStatus,
    TaskDuplicate,
    TaskTemplateChooser,
    TaskCreate
  },
  props: {
    elevation: {
      type: Number,
      default: 0,
      validator (value) {
        return value >= 0 && value <= 24
      }
    },
    header: String,
    loading: {
      type: Boolean,
      default: false
    },
    noDataText: {
      type: String,
      default: 'No tasks to display'
    },
    prototypes: {
      type: Array,
      default () {
        return []
      }
    },
    prototypingMode: {
      type: Boolean,
      default: false
    },
    tasks: {
      type: Array,
      default () {
        return []
      }
    },
    existingTasks: {
      type: Array,
      default () {
        return []
      }
    }
  },
  data () {
    return {
      addDialog: false,
      addMultipleDialog: false,
      duplicateDialog: false,
      templateDialog: false,
      internalPrototypes: this.prototypes,
      internalSelected: this.selected,
      showBulkActions: false,
      prototypeId: 0,
      headers: [
        { text: 'Hostname', value: 'hostname' },
        { text: 'Command', value: 'command' },
        { text: 'Status', value: 'status' },
        { text: 'PID', value: 'pid', align: 'right' },
        {
          text: 'Actions',
          value: 'name',
          align: 'right',
          sortable: false
        }
      ],
      pagination: {
        sortBy: 'hostname',
        descending: false,
        rowsPerPage: 10
      },
      chosenTemplate: '',
      editingTasks: []
    }
  },
  computed: {
    showAddButton () {
      if (this.prototypingMode) {
        return true
      }

      return this.internalSelected.length === 0
    },
    tasksPerformingCrud () {
      return Array.isArray(this.performingCrudAction)
        ? this.performingCrudAction
        : [this.performingCrudAction]
    }
  },
  watch: {
    internalSelected () {
      if (this.internalSelected.length) {
        this.showBulkActions = true
      } else {
        this.showBulkActions = false
      }
    }
  },
  methods: {
    editMultipleTasks () {
      this.editingTasks = this.internalSelected
      this.addMultipleDialog = true
    },
    openFromExisting (selectedTasks) {
      this.selectedTasks = selectedTasks
      this.duplicateDialog = false
      this.addMultipleDialog = true
    },
    openFromTemplate (chosenTemplate) {
      this.chosenTemplate = chosenTemplate
      this.addMultipleDialog = true
    },
    addPrototypes (tasks) {
      for (let task of tasks) {
        let newTask = { ...task, id: this.prototypeId++, status: 'prototype' }
        this.internalPrototypes.push(newTask)
      }
      this.addMultipleDialog = false
      this.$emit('updatePrototypes', this.internalPrototypes)
    },
    editTasks (tasks) {
      for (let newTask of tasks) {
        for (let oldTask of this.tasks) {
          if (newTask.id === oldTask.id) {
            oldTask = JSON.parse(JSON.stringify(newTask))
          }
        }
      }
      this.addMultipleDialog = false
      this.$emit('updateTasks', this.tasks)
    },
    removeTasks () {
      for (let selectedTask of this.internalSelected) {
        for (let taskIndex in this.tasks) {
          if (this.tasks[taskIndex].id === selectedTask.id) {
            this.tasks.splice(taskIndex, 1)
          }
        }
      }
      this.$emit('removeTasks', this.tasks)
    },
    addPrototype (task) {
      let newTask = { ...task, id: this.prototypeId++ }
      this.addDialog = false
      this.internalPrototypes.push(newTask)
      this.$emit('updatePrototypes', this.internalPrototypes)
    },
    removePrototype (id) {
      this.internalPrototypes = this.internalPrototypes.filter(
        task => task.id !== id
      )

      this.$emit('updatePrototypes', this.internalPrototypes)
    },
    isPerformingCrud (taskId) {
      return this.tasksPerformingCrud.includes(taskId)
    },
    emitCrudAction (task, action) {
      this.$emit('crud-action', task, action)
    }
  }
}
</script>

<style scoped>
/* This resets font weight set by Bootstrap to the default 'normal' value. */
/* The proper way of creating a deep selector would be using `::v-deep` but */
/* it requires Vue Loader v15 which we do not use for now. */
label {
  font-weight: normal;
}

.text-monospace {
  font-family: ui-monospace, "SF Mono", SFMono-Regular, "DejaVu Sans Mono",
    Liberation Mono, Menlo, Consolas, Monaco, monospace;
}

.text-tabular-nums {
  font-variant-numeric: tabular-nums;
}

.command-cell {
  max-width: 360px;
}

/* Sets the same font properties for prototypes */
table.v-table tfoot td {
  font-weight: 400;
  font-size: 13px;
}
</style>
