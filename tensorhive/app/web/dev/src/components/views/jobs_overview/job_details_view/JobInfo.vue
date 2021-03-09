<template>
  <v-container grid-list-md>
    <v-layout wrap>
      <NameSection
        :readOnly="readOnly"
        :name="job.name"
        @changeName="changeName"
      />
      <DescriptionSection
        :readOnly="readOnly"
        :description="job.description"
        @changeDescription="changeDescription"
      />
      <DateRangeSection
        :readOnly="readOnly"
        :startAt="job.startAt"
        :stopAt="job.stopAt"
        @changeStartAt="changeStartAt"
        @changeStopAt="changeStopAt"
      />
      <v-flex xs6 md2 v-if="readOnly">
        <JobDetailsField v-slot="props" header="Status" :value="job.status">
          <JobStatus class="ma-0" :status="props.value" />
        </JobDetailsField>
      </v-flex>

      <v-flex xs6 md2 v-if="readOnly">
        <JobDetailsField header="ID" :value="job.id" />
      </v-flex>
    </v-layout>
  </v-container>
</template>

<script>
import { required, maxLength } from '../../../../utils/rules'
import NameSection from './job_info/NameSection'
import DescriptionSection from './job_info/DescriptionSection'
import DateRangeSection from './job_info/DateRangeSection'
import JobDetailsField from './job_info/JobDetailsField'
import JobStatus from '../JobStatus'

const nameCounter = 40

export default {
  components: { NameSection, DescriptionSection, DateRangeSection, JobDetailsField, JobStatus },
  props: {
    readOnly: {
      type: Boolean,
      default: true
    },
    job: {
      type: Object,
      default () {
        return {
          name: undefined,
          description: undefined,
          startAt: undefined,
          stopAt: undefined
        }
      }
    }
  },
  data () {
    return {
      valid: false,
      nameCounter,
      nameRules: [required('name'), maxLength('name', nameCounter)]
    }
  },
  methods: {
    changeName (value) {
      this.job.name = value
      this.updateJob()
    },
    changeDescription (value) {
      this.job.description = value
      this.updateJob()
    },
    changeStartAt (value) {
      this.job.startAt = value
      this.updateJob()
    },
    changeStopAt (value) {
      this.job.stopAt = value
      this.updateJob()
    },
    updateJob () {
      this.$emit('changeJob', this.job)
    }
  }
}
</script>
