<template>
  <v-layout wrap v-if='readOnly'>
    <!-- This nested form is used to revalidate dates which depend -->
    <!-- on each other. Unfortunately, Vuetify currently does not -->
    <!-- have an option to validate a single field so such a hacky -->
    <!-- way of doing that is required here. -->
    <v-flex xs12 sm6 md4>
      <JobDetailsField header='Start at' :value='startAt' />
    </v-flex>
    <v-flex xs12 sm6 md4>
      <JobDetailsField header='Stop at' :value='stopAt' />
    </v-flex>
  </v-layout>
  <v-flex xs12 v-else>
    <v-form ref='dates'>
      <v-layout wrap>
        <v-flex xs12 sm6>
          <DatetimePicker
            v-model="startAtModel"
            :value='startAt'
            @change='changeStartAt'
            box
            label='Start at'
            :rules='startAtRules'
          />
        </v-flex>
        <v-flex xs12 sm6>
          <DatetimePicker
            :value='stopAt'
            @change='changeStopAt'
            box
            label='Stop at'
            :rules='stopAtRules'
          />
        </v-flex>
      </v-layout>
    </v-form>
  </v-flex>
</template>

<script>
import moment from 'moment'
import JobDetailsField from '../JobDetailsField'
import DatetimePicker from '../../../general/DatetimePicker'

export default {
  components: { JobDetailsField, DatetimePicker },
  props: {
    readOnly: Boolean,
    startAt: Date,
    stopAt: Date
  },
  data () {
    return {
      startAtModel: this.startAt,
      stopAtModel: this.stopAt
    }
  },
  watch: {
    startAtModel () {
      this.changeStartAt()
    },
    stopAtModel () {
      this.changeStopAt()
    }
  },
  computed: {
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

      if (this.stopAt) {
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
    changeStartAt () {
      this.$emit('changeStartAt', this.startAtModel)
      this.$refs.dates.validate()
    },
    changeStopAt () {
      this.$emit('changeStopAt', this.startAtModel)
      this.$refs.dates.validate()
    }
  }
}
</script>
