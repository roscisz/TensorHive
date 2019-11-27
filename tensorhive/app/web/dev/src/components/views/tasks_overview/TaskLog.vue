<template>
  <v-dialog
    width="80vw"
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
        <span class="headline">Task log</span>
      </v-card-text>
      <v-card-text>
        {{path}}
      <div class="log_box">
        <div v-for="(line, index) in lines" :key="index">
          {{line}}
        </div>
      </div>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>

<script>
export default {
  props: {
    showModal: Boolean,
    lines: Array,
    path: String
  },
  data () {
    return {
      show: false
    }
  },
  watch: {
    showModal () {
      this.show = this.showModal
    },
    show () {
      if (this.show === false) this.close()
    }
  },
  methods: {
    close: function () {
      this.$emit('close')
    }
  }
}
</script>

<style scoped>
.float-right-button {
  float: right;
}
.log_box{
  resize: both;
  background-color: #f8f9fa;
  border: 1px solid #eaecf0;
}
</style>
