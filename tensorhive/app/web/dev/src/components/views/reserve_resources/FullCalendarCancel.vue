<template>
  <v-layout row justify-center>
    <v-dialog
      width="600px"
      v-model="showModal"
    >
      <v-card>
        <v-card-title>
          Do you want to cancel this reservation?
        </v-card-title>
        <v-card-text>
          <v-btn
            color="error"
            small
            outline
            round
            @click="close()"
          >
            No
          </v-btn>
          <v-btn
            color="success"
            round
            @click="cancelReservation()"
          >
            Yes
          </v-btn>
        </v-card-text>
      </v-card>
    </v-dialog>
  </v-layout>
</template>

<script>
export default {
  name: 'FullCalendarCancel',

  props: {
    showModal: Boolean,
    reservation: Object,
    cancel: Function

  },

  methods: {
    close: function () {
      this.$emit('close')
    },

    cancelReservation: function () {
      this.cancel(this.reservation)
      this.close()
    }
  }
}
</script>
