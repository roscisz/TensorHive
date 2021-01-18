<template>
  <v-container class="pa-0">
    <v-layout class="mb-2" align-center>
      <h5 class="headline mx-2" v-if="header">{{ header }}</h5>

      <v-spacer v-if="header && prototypingMode"></v-spacer>

      <v-layout class="px-4" v-if="prototypingMode" align-center>
        <v-icon>info</v-icon>
        <div class="ml-2 caption grey--text text--darken-1">
          Newly added tasks have the <i>Prototype</i> status and they will be
          created along with this job.
        </div>
      </v-layout>

      <v-spacer></v-spacer>

      <v-flex v-if="showBulkActions" xs4>
        <TaskBulkActions
          :performing-action="performingBulkAction"
          :small-perform-button="smallPerformButton"
          @action="$emit('bulk-action', internalSelected, $event)"
        />
      </v-flex>

      <v-dialog
        v-if="showAddButton"
        v-model="addDialog"
        scrollable
        max-width="860px"
        width="60%"
      >
        <template v-slot:activator="{ on }">
          <v-btn v-on="on" color="primary" :small="smallAddButton">
            Add Task
          </v-btn>
        </template>

        <TaskAddForm
          @cancel="addDialog = false"
          @add="addPrototype"
          :chosen-template="chosenTemplate"
        />
      </v-dialog>
      <TaskCreate
        v-if="showAddButton && prototypingMode"
        :show-modal="addMultipleDialog"
        @close="addDialog=false"
        :chosen-template="chosenTemplate"
        @submit="addPrototypes"
      />
      <TaskTemplateChooser
        v-if="showAddButton && prototypingMode"
        :show-modal="templateDialog"
        @close="templateDialog=false"
        @openFromTemplate="openFromTemplate"
      />
    </v-layout>

    <v-layout>
      <v-flex xs12>
        <v-data-table
          v-bind:class="`elevation-${elevation}`"
          v-model="internalSelected"
          item-key="id"
          select-all
          :headers="headers"
          :items="tasks"
          :loading="loading"
          :no-data-text="noDataText"
          :pagination.sync="pagination"
          @input="$emit('update:selected', $event)"
        >
          <template v-slot:items="props">
            <tr>
              <td>
                <v-tooltip bottom>
                  <template v-slot:activator="{ on }">
                    <v-checkbox
                      v-on="on"
                      v-model="props.selected"
                      hide-details
                      color="primary"
                    ></v-checkbox>
                  </template>
                  <span v-if="props.selected">This task will be copied</span>
                  <span v-else>Select to copy this task into this job</span>
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
                  v-if="!prototypingMode"
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
import TaskAddForm from './TaskAddForm'
import TaskBulkActions from './TaskBulkActions'
import TaskCommand from './TaskCommand'
import TaskCrudActions from './TaskCrudActions'
import TaskStatus from './TaskStatus'
import TaskTemplateChooser from './TaskTemplateChooser'
import TaskCreate from './TaskCreate'

export default {
  components: {
    TaskAddForm,
    TaskBulkActions,
    TaskCommand,
    TaskCrudActions,
    TaskStatus,
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
    performingCrudAction: {
      type: [Number, Array],
      default () {
        return []
      }
    },
    performingBulkAction: {
      type: Boolean,
      default: false
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
    selected: {
      type: Array,
      default () {
        return []
      }
    },
    smallAddButton: {
      type: Boolean,
      default: false
    },
    smallPerformButton: {
      type: Boolean,
      default: false
    },
    tasks: {
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
      templateDialog: false,
      internalPrototypes: this.prototypes,
      internalSelected: this.selected,
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
      chosenTemplate: ''
    }
  },
  computed: {
    showBulkActions () {
      if (this.prototypingMode) {
        return false
      }

      return this.internalSelected.length > 0
    },
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
  methods: {
    openFromTemplate (chosenTemplate) {
      this.chosenTemplate = chosenTemplate
      this.addDialog = true
    },
    addPrototypes (tasks) {
      for (let task of tasks) {
        let newTask = { ...task, id: this.prototypeId++, status: 'prototype' }
        this.internalPrototypes.push(newTask)
      }
      debugger
      this.addMultipleDialog = false
      this.$emit('update:prototypes', this.internalPrototypes)
    },
    addPrototype (task) {
      let newTask = { ...task, id: this.prototypeId++ }
      this.addDialog = false
      if (this.prototypingMode) {
        this.internalPrototypes.push(newTask)
        this.$emit('update:prototypes', this.internalPrototypes)
      } else {
        this.$emit('add', newTask)
      }
    },
    removePrototype (id) {
      this.internalPrototypes = this.internalPrototypes.filter(
        task => task.id !== id
      )

      this.$emit('update:prototypes', this.internalPrototypes)
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
