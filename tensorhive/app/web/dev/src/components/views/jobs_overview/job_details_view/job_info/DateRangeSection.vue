<template>
  <v-layout wrap v-if="!editMode">
    <v-flex xs18 sm8 md6>
      <JobDetailsField header="Start at" :value="formatedStartAt" />
    </v-flex>
    <v-flex xs12 sm6 md4>
      <JobDetailsField header="Stop at" :value="formatedStopAt" />
    </v-flex>
  </v-layout>
  <v-flex xs12 v-else>
    <v-form ref="dates">
      <v-layout wrap>
        <v-flex xs12 sm6>
          <DatetimePicker
            :datetime="startAtEditMode"
            @input="changeStartAt"
            box
            label="Start at"
            :rules="startAtRules"
          />
        </v-flex>
        <v-flex xs12 sm6>
          <DatetimePicker
            :datetime="stopAt"
            @input="changeStopAt"
            box
            label="Stop at"
            :rules="stopAtRules"
          />
        </v-flex>
      </v-layout>
    </v-form>
  </v-flex>
</template>

<script>
import moment from 'moment'
import JobDetailsField from './JobDetailsField'
import DatetimePicker from '../../../../general/DatetimePicker'

export default {
  components: { JobDetailsField, DatetimePicker },
  props: {
    editMode: Boolean,
    startAt: String,
    stopAt: String
  },
  data () {
    return {
      pickersKey: 0
    }
  },
  computed: {
    formatedStartAt () {
      return this.startAt ? moment(this.startAt).format('YYYY-MM-DD HH:mm:ss') : ''
    },
    formatedStopAt () {
      return this.stopAt ? moment(this.stopAt).format('YYYY-MM-DD HH:mm:ss') : ''
    },
    startAtEditMode () {
      return this.startAt
    },
    startAtRules () {
      const rules = [
        (v) => {
          if (v) {
            return (
              moment(v).isSameOrAfter(moment()) ||
              'Start date cannot be set to past'
            )
          }

          return true
        }
      ]

      if (!this.startAt && this.stopAt) {
        rules.push(
          (v) =>
            !!v ||
            'Start date must be specified when the stop date is specified',
          (v) => {
            if (v) {
              return (
                moment(v).isSameOrBefore(this.stopAt) ||
                'Start date must be before the stop date'
              )
            }

            return true
          }
        )
      }

      return rules
    },
    stopAtRules () {
      const rules = [
        (v) => {
          if (v) {
            return (
              moment(v).isSameOrAfter(moment()) ||
              'Stop date cannot be set to past'
            )
          }

          return true
        }
      ]

      if (this.startAt && this.stopAt) {
        rules.push((v) => {
          if (v) {
            return (
              moment(v).isSameOrAfter(this.startAt) ||
              'Stop date must be after the start date'
            )
          }

          return true
        })
      }

      return rules
    }
  },
  methods: {
    changeStartAt (value) {
      this.$emit('changeStartAt', value)
      this.$refs.dates.validate()
    },
    changeStopAt (value) {
      this.$emit('changeStopAt', value)
      this.$refs.dates.validate()
    }
  }
}
</script>
