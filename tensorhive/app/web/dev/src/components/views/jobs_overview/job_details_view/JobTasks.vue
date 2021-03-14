<template>
  <v-container class="pa-0">
    <v-layout class="mb-2" align-center>
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
            @click="removeTasks(selectedTasks)"
          >
            <v-icon small>delete</v-icon>
          </v-btn>
        </template>
        <span>Remove selected tasks</span>
      </v-tooltip>
      <v-spacer></v-spacer>
      <TaskCreate
        v-if="editMode"
        :show-modal="addMultipleDialog"
        :chosen-template="chosenTemplate"
        :selected-tasks="selectedExistingTasks"
        :editing-tasks="editingTasks"
        @open="addMultipleDialog = true"
        @close="addMultipleDialog = false; chosenTemplate = ''; selectedExistingTasks = []; editingTasks = []"
        @add="addTasks"
        @edit="updateTasks"
      />
      <TaskTemplateChooser
        v-if="editMode"
        :show-modal="templateDialog"
        @open="templateDialog = true"
        @close="templateDialog = false"
        @openFromTemplate="openFromTemplate"
      />
      <TaskDuplicate
        v-if="editMode"
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
          v-model="selectedTasks"
          item-key="id"
          :select-all="editMode"
          :headers="headers"
          :items="tasks"
          :loading="loading"
          :no-data-text="noDataText"
          :pagination.sync="pagination"
        >
          <template v-slot:items="props">
            <tr>
              <td v-if="editMode">
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
                <TaskCommand no-command-text :command="props.item.command" />
              </td>
              <td>
                <TaskStatus class="ma-0" :status="props.item.status" />
              </td>
              <td class="text-tabular-nums text-xs-right">{{ props.item.pid }}</td>
              <td>
                <v-layout align-center justify-end>
                  <TaskLog
                    v-if="!editMode"
                    :show-modal="logDialog"
                    @open="logDialog = true"
                    @close="logDialog = false"
                    :taskId="props.item.id"
                  />
                  <v-tooltip v-if="editMode" bottom>
                    <template v-slot:activator="{ on }">
                      <v-btn
                        class="ma-0"
                        v-on="on"
                        flat
                        icon
                        small
                        color="grey"
                        @click="editTask(props.item)"
                      >
                        <v-icon small>edit</v-icon>
                      </v-btn>
                    </template>
                    <span>Edit this task</span>
                  </v-tooltip>
                  <v-tooltip v-if="editMode" bottom>
                    <template v-slot:activator="{ on }">
                      <v-btn
                        class="ma-0"
                        v-on="on"
                        flat
                        icon
                        small
                        color="grey"
                        @click="removeTasks([props.item])"
                      >
                        <v-icon small>delete</v-icon>
                      </v-btn>
                    </template>
                    <span>Remove this task</span>
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
import TaskCommand from './job_tasks/TaskCommand'
import TaskStatus from './job_tasks/TaskStatus'
import TaskDuplicate from './job_tasks/TaskDuplicate'
import TaskTemplateChooser from './job_tasks/TaskTemplateChooser'
import TaskCreate from './job_tasks/TaskCreate'
import TaskLog from './job_tasks/TaskLog'

export default {
  components: {
    TaskCommand,
    TaskStatus,
    TaskDuplicate,
    TaskTemplateChooser,
    TaskCreate,
    TaskLog
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
    editMode: {
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
      addMultipleDialog: false,
      duplicateDialog: false,
      templateDialog: false,
      logDialog: false,
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
      selectedTasks: [],
      editingTasks: [],
      selectedExistingTasks: []
    }
  },
  computed: {
    tasksPerformingCrud () {
      return Array.isArray(this.performingCrudAction)
        ? this.performingCrudAction
        : [this.performingCrudAction]
    }
  },
  watch: {
    selectedTasks () {
      if (this.selectedTasks.length) {
        this.showBulkActions = true
      } else {
        this.showBulkActions = false
      }
    }
  },
  methods: {
    editTask (task) {
      this.editingTasks = [task]
      this.addMultipleDialog = true
    },
    editMultipleTasks () {
      this.editingTasks = this.selectedTasks
      this.addMultipleDialog = true
    },
    openFromExisting (selectedTasks) {
      this.selectedExistingTasks = selectedTasks
      this.duplicateDialog = false
      this.addMultipleDialog = true
    },
    openFromTemplate (chosenTemplate) {
      this.chosenTemplate = chosenTemplate
      this.addMultipleDialog = true
    },
    addTasks (tasksToAdd) {
      this.addMultipleDialog = false
      this.$emit('addTasks', tasksToAdd)
    },
    updateTasks (tasksToUpdate) {
      this.editingTasks = []
      this.addMultipleDialog = false
      this.$emit('updateTasks', tasksToUpdate)
    },
    removeTasks (tasksToRemove) {
      this.$emit('removeTasks', tasksToRemove)
    },
    isPerformingCrud (taskId) {
      return this.tasksPerformingCrud.includes(taskId)
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
