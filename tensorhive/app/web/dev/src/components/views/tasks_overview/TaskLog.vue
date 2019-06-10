<template>
  <v-dialog
    persistent
    width="80vw"
    v-model="showModal"
  >
    <v-card>
      <v-card-title>
        <span class="headline">Task log</span>
      </v-card-title>
      <v-card-text>
        {{path}}
      <div class="log_box">
        <div v-for="(line, index) in lines" :key="index">
          {{line}}
        </div>
      </div>
      </v-card-text>
      <v-card-text>
        <v-layout align-center justify-end>
          <v-btn
            color="info"
            small
            outline
            round
            @click="close"
          >
            Close
          </v-btn>
        </v-layout>
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

  methods: {
    close: function () {
      this.$emit('close')
    }
  }
}
</script>

<style scoped>
.log_box{
  resize: both;
  background-color: #f8f9fa;
  border: 1px solid #eaecf0;
}
</style>
