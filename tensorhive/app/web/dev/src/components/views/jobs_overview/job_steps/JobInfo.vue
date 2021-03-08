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
    </v-layout>
  </v-container>
</template>

<script>
import { required, maxLength } from '../../../../utils/rules'
import NameSection from './NameSection'
import DescriptionSection from './DescriptionSection'
import DateRangeSection from './DateRangeSection'

const nameCounter = 40

export default {
  components: { NameSection, DescriptionSection, DateRangeSection },
  props: {
    readOnly: {
      type: Boolean,
      default: true
    },
    backButton: {
      type: Boolean,
      default: true
    },
    backButtonText: {
      type: String,
      default: 'Back'
    },
    backButtonLoading: Boolean,
    continueButton: {
      type: Boolean,
      default: true
    },
    continueButtonText: {
      type: String,
      default: 'Continue'
    },
    continueButtonLoading: Boolean,
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
