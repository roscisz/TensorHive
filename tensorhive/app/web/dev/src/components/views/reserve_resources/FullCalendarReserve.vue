<template>
  <v-layout row justify-center>
    <v-dialog
      width="50vw"
      v-model="show"
    >
      <v-card>
        <v-card-text>
          <v-btn
            class="float-right-button"
            flat
            icon
            color="black"
            @click="close()"
          >
            <v-icon>close</v-icon>
          </v-btn>
          <span class="headline">Which resources do you want to reserve?</span>
        </v-card-text>
        <v-card-text>
          <div
            class="resources_row"
            v-for="checkbox in resourcesCheckboxes"
            :key="checkbox.uuid"
          >
            <v-checkbox
              :label="`${checkbox.nodeName} GPU${ checkbox.index } ${ checkbox.name }`"
              v-model="checkbox.checked"
              :disabled="checkbox.disabled"
            >
            </v-checkbox>
          </div>
        </v-card-text>
        <v-card-text>
          <v-layout align-center justify-start>
            <v-menu
              v-model="startDateMenu"
              :close-on-content-click="false"
              :nudge-right="40"
              lazy
              transition="none"
              offset-y
              full-width
              min-width="290px"
            >
              <template v-slot:activator="{ on }">
                <v-text-field
                  v-model="newStartDate"
                  label="Start date"
                  prepend-icon="event"
                  v-on="on"
                ></v-text-field>
              </template>
              <v-date-picker
                v-model="newStartDate"
                @input="startDateMenu = false"
              ></v-date-picker>
            </v-menu>
            <v-menu
              ref="startMenu"
              v-model="startTimeMenu"
              :close-on-content-click="false"
              :nudge-right="40"
              :return-value.sync="newStartTime"
              lazy
              transition="none"
              offset-y
              full-width
              max-width="290px"
              min-width="290px"
            >
              <template v-slot:activator="{ on }">
                <v-text-field
                  v-model="newStartTime"
                  label="Start time"
                  prepend-icon="access_time"
                  v-on="on"
                ></v-text-field>
              </template>
              <v-time-picker
                v-if="startTimeMenu"
                v-model="newStartTime"
                full-width
                :allowed-minutes="m => m % 30 === 0"
                format="24hr"
                @click:minute="$refs.startMenu.save(newStartTime)"
              ></v-time-picker>
            </v-menu>
          </v-layout>
          <v-layout align-center justify-start>
            <v-menu
              v-model="endDateMenu"
              :close-on-content-click="false"
              :nudge-right="40"
              lazy
              transition="none"
              offset-y
              full-width
              min-width="290px"
            >
              <template v-slot:activator="{ on }">
                <v-text-field
                  v-model="newEndDate"
                  label="End date"
                  prepend-icon="event"
                  v-on="on"
                ></v-text-field>
              </template>
              <v-date-picker
                v-model="newEndDate"
                @input="endDateMenu = false"
              ></v-date-picker>
            </v-menu>
            <v-menu
              ref="endMenu"
              v-model="endTimeMenu"
              :close-on-content-click="false"
              :nudge-right="40"
              :return-value.sync="newEndTime"
              lazy
              transition="none"
              offset-y
              full-width
              max-width="290px"
              min-width="290px"
            >
              <template v-slot:activator="{ on }">
                <v-text-field
                  v-model="newEndTime"
                  label="End time"
                  prepend-icon="access_time"
                  v-on="on"
                ></v-text-field>
              </template>
              <v-time-picker
                v-if="endTimeMenu"
                v-model="newEndTime"
                full-width
                :allowed-minutes="m => m % 30 === 0"
                format="24hr"
                @click:minute="$refs.endMenu.save(newEndTime)"
              ></v-time-picker>
            </v-menu>
          </v-layout>
          <v-textarea
            outline
            label="Title"
            v-model="reservationTitle"
          ></v-textarea>
          <v-textarea
            outline
            label="Description"
            v-model="reservationDescription"
          ></v-textarea>
          <div v-show="showInfo===true" class="text-red"><p class="vertical-5p lead">You need to choose at least one resource to reserve</p></div>
          <div class="modal-footer text-right">
            <v-btn
              color="success"
              round
              @click="reservation()"
            >
              Reserve
            </v-btn>
          </div>
        </v-card-text>
      </v-card>
    </v-dialog>
  </v-layout>
</template>

<script>
import moment from 'moment'
export default {
  name: 'FullCalendarReserve',

  props: {
    showModal: Boolean,
    startDate: Date,
    endDate: Date,
    resourcesCheckboxes: Array,
    numberOfResources: Number,
    addReservation: Function

  },

  watch: {
    showModal () {
      this.show = this.showModal
    },
    show () {
      if (this.show === false) this.close()
    },

    startDate () {
      if (this.startTime !== null) {
        this.newStartDate = moment(this.startDate).format('YYYY-MM-DD')
        this.newStartTime = moment(this.startDate).format('HH:mm')
      } else {
        this.newStartDate = ''
        this.newStartTime = ''
      }
    },

    endDate () {
      if (this.endTime !== null) {
        this.newEndDate = moment(this.endDate).format('YYYY-MM-DD')
        this.newEndTime = moment(this.endDate).format('HH:mm')
      } else {
        this.newEndDate = ''
        this.newEndTime = ''
      }
    }
  },

  data () {
    return {
      startTimeMenu: false,
      startDateMenu: false,
      endTimeMenu: false,
      endDateMenu: false,
      newStartDate: '',
      newStartTime: '',
      newEndDate: '',
      newEndTime: '',
      showInfo: false,
      reservationTitle: '',
      reservationDescription: '',
      show: false
    }
  },

  methods: {
    close: function () {
      this.showInfo = false
      this.$emit('close')
    },

    anyChecked: function () {
      var anyChecked = false
      for (var checkbox in this.resourcesCheckboxes) {
        if (this.resourcesCheckboxes[checkbox].checked) {
          anyChecked = true
          break
        }
      }
      return anyChecked
    },

    reservation: function () {
      var tempReservation
      if (this.anyChecked()) {
        for (var i = 0; i < this.numberOfResources; i++) {
          if (this.resourcesCheckboxes[i].checked) {
            tempReservation = {
              title: this.reservationTitle,
              description: this.reservationDescription,
              start: moment(this.newStartDate + 'T' + this.newStartTime).toISOString(),
              end: moment(this.newEndDate + 'T' + this.newEndTime).toISOString(),
              resourceId: this.resourcesCheckboxes[i].uuid,
              userId: parseInt(this.$store.state.id)
            }
            this.addReservation(tempReservation)
          }
        }
      } else {
        this.showInfo = true
      }
    }
  }
}
</script>

<style scoped>
.float-right-button {
  float: right;
}
.resources_row{
  max-height: 25px;
}
</style>
