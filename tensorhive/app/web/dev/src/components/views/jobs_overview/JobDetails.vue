<template>
  <v-container class="pa-0">
    <v-layout class="mb-2">
      <v-flex xs12>
        <h5 class="headline mx-2">Job details</h5>
      </v-flex>
    </v-layout>

    <v-layout>
      <v-flex xs12>
        <v-sheet :elevation="1">
          <v-container class="px-2 py-3" grid-list-lg>
            <v-layout class="px-2" v-if="loading" align-center justify-center>
              <v-progress-circular
                indeterminate
                color="primary"
                :size="48"
              ></v-progress-circular>
            </v-layout>

            <template v-else>
              <v-layout class="px-1 mb-4" row wrap>
                <v-flex xs12 sm6 md4>
                  <JobDetailsField header="Name" :value="job.name" />
                </v-flex>

                <v-flex xs12 sm6 md8>
                  <JobDetailsField
                    v-slot="props"
                    header="Description"
                    :value="job.description"
                  >
                    <div class="job-description">{{ props.value }}</div>
                  </JobDetailsField>
                </v-flex>

                <v-flex xs12 sm6 md4>
                  <JobDetailsField header="Start at" :value="job.startAt" />
                </v-flex>

                <v-flex xs12 sm6 md4>
                  <JobDetailsField header="Stop at" :value="job.stopAt" />
                </v-flex>

                <v-flex xs6 md2>
                  <JobDetailsField
                    v-slot="props"
                    header="Status"
                    :value="job.status"
                  >
                    <JobStatus class="ma-0" :status="props.value" />
                  </JobDetailsField>
                </v-flex>

                <v-flex xs6 md2>
                  <JobDetailsField header="ID" :value="job.id" />
                </v-flex>
              </v-layout>

              <v-layout class="px-3">
                <v-flex xs12>
                  <JobCrudActions
                    :job-id="job.id"
                    :performing-action="performingCrudAction"
                    :show-details-action="false"
                    @action="$emit('crud-action', job, $event)"
                  />
                </v-flex>
              </v-layout>
            </template>
          </v-container>
        </v-sheet>
      </v-flex>
    </v-layout>
  </v-container>
</template>

<script>
import JobCrudActions from './JobCrudActions'
import JobDetailsField from './JobDetailsField'
import JobStatus from './JobStatus'

export default {
  components: { JobCrudActions, JobDetailsField, JobStatus },
  props: {
    job: Object,
    loading: {
      type: Boolean,
      default: false
    },
    performingCrudAction: {
      type: Boolean,
      default: false
    }
  }
}
</script>

<style scoped>
.text-monospace {
  font-family: ui-monospace, "SF Mono", SFMono-Regular, "DejaVu Sans Mono",
    Liberation Mono, Menlo, Consolas, Monaco, monospace;
}

.job-description {
  max-height: 280px;
  overflow-y: auto;
  white-space: pre-line;
}
</style>
