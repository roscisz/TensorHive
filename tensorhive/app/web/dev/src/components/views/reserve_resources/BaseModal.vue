<template>
  <transition name="modal">
    <div
      class="modal-mask"
      @click="close"
      v-show="show"
    >
      <div
        class="modal-container"
        @click.stop
      >
        <slot></slot>
      </div>
    </div>
  </transition>
</template>

<script>
export default {
  name: 'BaseModal',

  props: {
    show: Boolean
  },

  methods: {
    close: function () {
      this.$emit('close')
    }
  },

  mounted: function () {
    document.addEventListener('keydown', (e) => {
      if (this.show && e.keyCode === 27) {
        this.close()
      }
    })
  }
}
</script>

<style scoped>
.modal-fade-enter,
* {
  box-sizing: border-box;
}

.modal-mask {
  position: fixed;
  z-index: 9998;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, .5);
  transition: opacity .3s ease;
}

.modal-container {
  width: 70%;
  margin: 40px auto 0;
  padding: 20px 30px;
  background-color: #fff;
  border-radius: 2px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, .33);
  transition: all .3s ease;
  font-family: Helvetica, Arial, sans-serif;
}

.modal-header h3 {
  margin-top: 0;
  color: #42b983;
}

.modal-body {
  margin: 20px 0;
}

.text-right {
  text-align: right;
}

.form-label {
  display: block;
  margin-bottom: 1em;
}

.form-label > .form-control {
  margin-top: 0.5em;
}

.form-control {
  display: block;
  width: 100%;
  padding: 0.5em 1em;
  line-height: 1.5;
  border: 1px solid #ddd;
}

.modal-enter {
  opacity: 0;
}

.modal-leave-active {
  opacity: 0;
}

.modal-enter .modal-container,
.modal-leave-active .modal-container {
  -webkit-transform: scale(1.1);
  transform: scale(1.1);
}
</style>
