<template>
  <v-layout align-center justify-end>
    <v-dialog v-model="editDialog" scrollable max-width="860px" width="60%">
      <template v-slot:activator="{ on: onDialog }">
        <v-tooltip bottom>
          <template v-slot:activator="{ on: onTooltip }">
            <!-- Disabling these rules here since they are bugged. See also: -->
            <!-- https://github.com/vuejs/eslint-plugin-vue/issues/497 -->
            <!-- eslint-disable vue/valid-v-on vue/no-parsing-error -->
            <v-btn
              class="ma-0"
              v-on="{ ...onTooltip, ...onDialog }"
              flat
              icon
              small
              color="grey"
              :readonly="performingAction"
            >
              <!-- eslint-enable vue/valid-v-on vue/no-parsing-error -->
              <v-icon small>edit</v-icon>
            </v-btn>
          </template>
          <span>Edit this task</span>
        </v-tooltip>
      </template>

      <TaskEditForm
        :task="task"
        @cancel="editDialog = false"
        @edit="editTask"
      />
    </v-dialog>

    <!-- <v-tooltip bottom>
      <template v-slot:activator="{ on }">
        <v-btn
          class="ma-0"
          v-on="on"
          flat
          icon
          small
          color="grey"
          :readonly="performingAction"
          @click="$emit('action', task, TaskCrudActions.Execute)"
        >
          <v-icon small>play_arrow</v-icon>
        </v-btn>
      </template>
      <span>Execute this task</span>
    </v-tooltip>

    <v-tooltip bottom>
      <template v-slot:activator="{ on }">
        <v-btn
          class="ma-0"
          v-on="on"
          flat
          icon
          small
          color="grey"
          :readonly="performingAction"
          @click="$emit('action', task, TaskCrudActions.Stop)"
        >
          <v-icon small>stop</v-icon>
        </v-btn>
      </template>
      <span>Stop this task</span>
    </v-tooltip>

    <v-tooltip bottom>
      <template v-slot:activator="{ on }">
        <v-btn
          class="ma-0"
          v-on="on"
          flat
          icon
          small
          color="grey"
          :readonly="performingAction"
          @click="$emit('action', task, TaskCrudActions.Kill)"
        >
          <v-icon small>cancel</v-icon>
        </v-btn>
      </template>
      <span>Kill this task</span>
    </v-tooltip> -->

    <v-tooltip bottom>
      <template v-slot:activator="{ on }">
        <v-btn
          class="ma-0"
          v-on="on"
          flat
          icon
          small
          color="grey"
          :readonly="performingAction"
          @click="$emit('action', task, TaskCrudActions.Delete)"
        >
          <v-icon small>delete</v-icon>
        </v-btn>
      </template>
      <span>Remove this task</span>
    </v-tooltip>

    <v-tooltip v-if="showDetailsAction" bottom>
      <template v-slot:activator="{ on }">
        <v-btn
          class="ma-0"
          v-on="on"
          flat
          icon
          small
          color="primary"
          :readonly="performingAction"
          @click="$emit('action', task, TaskCrudActions.Details)"
        >
          <v-icon>chevron_right</v-icon>
        </v-btn>
      </template>
      <span>View task details</span>
    </v-tooltip>
  </v-layout>
</template>

<script>
import TaskEditForm from './TaskEditForm'

export const TaskCrudActions = {
  Edit: 'Edit',
  Execute: 'Execute',
  Stop: 'Stop',
  Kill: 'Kill',
  Delete: 'Delete'
}

export default {
  components: { TaskEditForm },
  props: {
    task: {
      type: Object,
      required: true
    },
    performingAction: {
      type: Boolean,
      default: false
    },
    showDetailsAction: {
      type: Boolean,
      default: true
    }
  },
  data () {
    return {
      TaskCrudActions: TaskCrudActions,
      editDialog: false,
      detailsDialog: false
    }
  },
  methods: {
    editTask (task) {
      this.editDialog = false

      this.$emit('action', task, TaskCrudActions.Edit)
    }
  }
}
</script>
