<template>
  <div>
    <h5 class="headline">Basic information about the new job</h5>
    <v-form ref="form" v-model="valid">
      <v-container grid-list-md>
        <v-layout wrap>
          <v-flex xs12>
            <v-text-field
              v-model="job.name"
              box
              persistent-hint
              required
              hint="*Required"
              label="Name*"
              :counter="nameCounter"
              :rules="nameRules"
            ></v-text-field>
          </v-flex>
          <v-flex xs12>
            <v-textarea
              v-model="job.description"
              auto-grow
              box
              label="Description"
              rows="4"
            ></v-textarea>
          </v-flex>
          <v-flex xs12>
            <!-- This nested form is used to revalidate dates which depend -->
            <!-- on each other. Unfortunately, Vuetify currently does not -->
            <!-- have an option to validate a single field so such a hacky -->
            <!-- way of doing that is required here. -->
            <v-form ref="dates">
              <v-layout wrap>
                <v-flex xs12 sm6>
                  <DatetimePicker
                    v-model="job.startAt"
                    box
                    label="Start at"
                    :rules="startAtRules"
                  />
                </v-flex>
                <v-flex xs12 sm6>
                  <DatetimePicker
                    v-model="job.stopAt"
                    box
                    label="Stop at"
                    :rules="stopAtRules"
                  />
                </v-flex>
              </v-layout>
            </v-form>
          </v-flex>
        </v-layout>

        <v-layout v-if="backButton || continueButton">
          <v-btn
            v-if="backButton"
            flat
            color="primary"
            :loading="backButtonLoading"
            @click="$emit('back')"
          >
            {{ backButtonText }}
          </v-btn>
          <v-spacer></v-spacer>
          <v-btn
            v-if="continueButton"
            color="primary"
            :loading="continueButtonLoading"
            @click="continueStep"
          >
            {{ continueButtonText }}
          </v-btn>
        </v-layout>
      </v-container>
    </v-form>
  </div>
</template>

<script>
import moment from 'moment'
import { required, maxLength } from '../../../../utils/rules'
import DatetimePicker from '../../../general/DatetimePicker'

const nameCounter = 40

export default {
  components: { DatetimePicker },
  props: {
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
  computed: {
    startAtRules () {
      const rules = [
        v => {
          if (v) {
            return (
              moment(v).isSameOrAfter(moment()) ||
              'Start date cannot be set to past'
            )
          }

          return true
        }
      ]

      if (this.job.stopAt) {
        rules.push(
          v =>
            !!v ||
            'Start date must be specified when the stop date is specified',
          v => {
            if (v) {
              return (
                moment(v).isSameOrBefore(this.job.stopAt) ||
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
        v => {
          if (v) {
            return (
              moment(v).isSameOrAfter(moment()) ||
              'Stop date cannot be set to past'
            )
          }

          return true
        }
      ]

      if (this.job.startAt && this.job.stopAt) {
        rules.push(v => {
          if (v) {
            return (
              moment(v).isSameOrAfter(this.job.startAt) ||
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
    continueStep () {
      if (this.$refs.form.validate()) {
        this.$emit('continue', this.job)
      }
    }
  },
  watch: {
    'job.startAt' () {
      this.$refs.dates.validate()
    },
    'job.stopAt' () {
      this.$refs.dates.validate()
    }
  }
}
</script>
