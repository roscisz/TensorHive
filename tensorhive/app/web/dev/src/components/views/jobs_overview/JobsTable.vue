<template>
  <v-container class="pa-0">
    <v-layout class="mb-2">
      <h5 class="headline mx-2" v-if="header">{{ header }}</h5>
      <v-spacer></v-spacer>
      <v-flex v-if="internalSelected.length > 0" xs4>
        <JobBulkActions
          :performing-action="performingBulkAction"
          :small-perform-button="smallPerformButton"
          @action="$emit('bulk-action', internalSelected, $event)"
        />
      </v-flex>
      <v-btn v-else color="primary" to="/job/add" :small="smallAddButton">
        Add Job
      </v-btn>
    </v-layout>

    <v-layout>
      <v-flex xs12>
        <v-data-table
          v-bind:class="`elevation-${elevation}`"
          v-model="internalSelected"
          select-all
          item-key="id"
          no-data-text="No jobs to display"
          :headers="headers"
          :items="jobs"
          :loading="loading"
          :pagination.sync="pagination"
          @input="$emit('update:selectedJobs', $event)"
        >
          <template v-slot:items="props">
            <tr>
              <td>
                <v-checkbox
                  v-model="props.selected"
                  hide-details
                  color="primary"
                ></v-checkbox>
              </td>

              <td>{{ props.item.name }}</td>

              <td class="text-monospace">
                <JobUser
                  :userId="props.item.userId"
                  @error="$emit('error', $event)"
                />
              </td>

              <td>
                <JobStatus class="ma-0" :status="props.item.status" />
              </td>

              <td>
                <JobCrudActions
                  :job-id="props.item.id"
                  :performing-action="isPerformingCrud(props.item.id)"
                  @action="$emit('crud-action', props.item, $event)"
                />
              </td>
            </tr>
          </template>
        </v-data-table>
      </v-flex>
    </v-layout>
  </v-container>
</template>

<script>
import JobBulkActions from './JobBulkActions'
import JobCrudActions from './JobCrudActions'
import JobStatus from './JobStatus'
import JobUser from './JobUser'

export default {
  components: {
    JobBulkActions,
    JobCrudActions,
    JobStatus,
    JobUser
  },
  props: {
    elevation: {
      type: Number,
      default: 0,
      validator (value) {
        return value >= 0 && value <= 24
      }
    },
    loading: {
      type: Boolean,
      default: false
    },
    header: String,
    jobs: {
      type: Array,
      default () {
        return []
      }
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
    }
  },
  data () {
    return {
      internalSelected: this.selected,
      headers: [
        { text: 'Name', value: 'name' },
        { text: 'User', value: 'username' },
        { text: 'Status', value: 'status' },
        { text: 'Actions', value: 'name', align: 'right', sortable: false }
      ],
      pagination: {
        sortBy: 'name',
        descending: false,
        rowsPerPage: 10
      }
    }
  },
  computed: {
    jobsPerformingCrud () {
      return Array.isArray(this.performingCrudAction)
        ? this.performingCrudAction
        : [this.performingCrudAction]
    }
  },
  methods: {
    isPerformingCrud (jobId) {
      return this.jobsPerformingCrud.includes(jobId)
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

.text-monospace {
  font-family: ui-monospace, "SF Mono", SFMono-Regular, "DejaVu Sans Mono",
    Liberation Mono, Menlo, Consolas, Monaco, monospace;
}
</style>
