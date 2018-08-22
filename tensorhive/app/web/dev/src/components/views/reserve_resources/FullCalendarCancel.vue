<template>
  <BaseModal
    :show="showModal"
    @close="close"
  >
    <div class="modal-header">
      <h3>Do you want to cancel this reservation?</h3>
    </div>
    <div class="modal-body">
    </div>
    <div class="modal-footer text-right">
      <button
        class="modal-default-button"
        @click="cancelReservation()"
      >
        Yes
      </button>
      <button
        class="modal-default-button"
        @click="close()"
      >
        No
      </button>
    </div>
  </BaseModal>
</template>

<script>
import BaseModal from './BaseModal.vue'
export default {
  name: 'FullCalendarCancel',

  props: {
    showModal: Boolean,
    reservation: Object,
    cancel: Function

  },

  components: {
    BaseModal
  },

  data () {
    return {
      title: '',
      body: ''
    }
  },

  methods: {
    close: function () {
      this.$emit('close')
      this.title = ''
      this.body = ''
    },

    cancelReservation: function () {
      this.cancel(this.reservation)
      this.close()
    }
  }
}
</script>
