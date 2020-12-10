<!-- This component was inspired by a similar component from the -->
<!-- 'vuetify-datetime-picker' package published on npm -->
<template>
  <v-dialog v-model="visible" :width="width">
    <template v-slot:activator="{ on }">
      <v-text-field
        v-on="on"
        readonly
        :box="box"
        :disabled="disabled"
        :hint="hint"
        :label="label"
        :outline="outline"
        :rules="rules"
        :solo="solo"
        :value="formattedDatetime"
      ></v-text-field>
    </template>

    <v-card>
      <v-card-text class="px-0">
        <v-tabs v-model="activeTab" fixed-tabs>
          <v-tab key="calendar">
            <v-icon>event</v-icon>
          </v-tab>
          <v-tab key="timer" :disabled="!date">
            <v-icon>access_time</v-icon>
          </v-tab>

          <v-tab-item key="calendar">
            <v-card flat>
              <v-card-text>
                <v-date-picker
                  v-model="date"
                  full-width
                  @input="activeTab = 1"
                ></v-date-picker>
              </v-card-text>
            </v-card>
          </v-tab-item>
          <v-tab-item key="timer">
            <v-card flat>
              <v-card-text>
                <v-time-picker
                  ref="timer"
                  v-model="time"
                  full-width
                  format="24hr"
                  :use-seconds="pickSeconds"
                ></v-time-picker>
              </v-card-text>
            </v-card>
          </v-tab-item>
        </v-tabs>
      </v-card-text>

      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn flat color="primary" @click="reset">Clear</v-btn>
        <v-btn color="primary" @click="submit">Ok</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import moment from 'moment'

const defaultDate = null
const defaultTime = '00:00:00'
const defaultDateFormat = 'YYYY-MM-DD'
const defaultTimeFormat = 'HH:mm:ss'
const defaultWidth = '380px'

export default {
  model: {
    prop: 'datetime',
    event: 'input'
  },
  props: {
    box: Boolean,
    datetime: [Date, String, moment],
    dateFormat: {
      type: String,
      default: defaultDateFormat
    },
    disabled: Boolean,
    hint: String,
    label: String,
    outline: Boolean,
    pickSeconds: {
      type: Boolean,
      default: true
    },
    rules: Array,
    solo: Boolean,
    timeFormat: {
      type: String,
      default: defaultTimeFormat
    },
    width: {
      type: [String, Number],
      default: defaultWidth
    }
  },
  data () {
    return {
      visible: false,
      activeTab: 0,
      date: defaultDate,
      time: defaultTime
    }
  },
  computed: {
    selectedDatetime () {
      if (this.date && this.time) {
        return moment(`${this.date} ${this.time}`)
      }

      return null
    },
    formattedDatetime () {
      const date = this.selectedDatetime

      return date ? date.format(`${this.dateFormat} ${this.timeFormat}`) : ''
    }
  },
  methods: {
    reset () {
      this.activeTab = 0
      this.date = defaultDate
      this.time = defaultTime

      this.$emit('input', undefined)
    },
    submit () {
      this.visible = false
      this.activeTab = 0

      this.$emit('input', this.selectedDatetime)
    }
  }
}
</script>
