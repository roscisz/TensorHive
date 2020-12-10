<template>
  <v-layout align-center justify-end>
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
          :to="`/job/${jobId}/edit`"
        >
          <v-icon small>edit</v-icon>
        </v-btn>
      </template>
      <span>Edit this job</span>
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
          @click="$emit('action', JobCrudActions.Execute)"
        >
          <v-icon small>play_arrow</v-icon>
        </v-btn>
      </template>
      <span>Execute job tasks</span>
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
          @click="$emit('action', JobCrudActions.Stop)"
        >
          <v-icon small>stop</v-icon>
        </v-btn>
      </template>
      <span>Stop job tasks</span>
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
          @click="$emit('action', JobCrudActions.Kill)"
        >
          <v-icon small>cancel</v-icon>
        </v-btn>
      </template>
      <span>Kill job tasks</span>
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
          @click="$emit('action', JobCrudActions.Delete)"
        >
          <v-icon small>delete</v-icon>
        </v-btn>
      </template>
      <span>Remove this job</span>
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
          :to="`/job/${jobId}`"
        >
          <v-icon>chevron_right</v-icon>
        </v-btn>
      </template>
      <span>View job details</span>
    </v-tooltip>
  </v-layout>
</template>

<script>
export const JobCrudActions = {
  Execute: 'Execute',
  Stop: 'Stop',
  Kill: 'Kill',
  Delete: 'Delete'
}

export default {
  props: {
    jobId: {
      type: Number,
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
      JobCrudActions: JobCrudActions
    }
  }
}
</script>
