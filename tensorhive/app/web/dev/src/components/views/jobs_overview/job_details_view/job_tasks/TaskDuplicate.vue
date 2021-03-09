<template>
  <v-dialog width="80vw" v-model="showModal">
    <template v-slot:activator="{ on }">
      <v-btn
        v-on="on"
        color="primary"
        small
        @click="$emit('open')"
      >Duplicate tasks</v-btn>
    </template>
    <v-card>
      <v-card-text>
        <v-btn
          class="float-right-button"
          flat
          icon
          color="black"
          @click="close"
        >
          <v-icon>close</v-icon>
        </v-btn>
        <span class="headline">Choose framework template</span>
      </v-card-text>
      <v-card-text>
        <v-layout>
          <v-flex xs12>
            <v-data-table
              v-bind:class="`elevation-${elevation}`"
              v-model="selectedTasks"
              item-key="id"
              select-all
              :headers="headers"
              :items="existingTasks"
              :loading="loading"
              :no-data-text="noDataText"
              :pagination.sync="pagination"
              @input="$emit('update:selected', $event)"
            >
              <template v-slot:items="props">
                <tr>
                  <td>
                    <v-checkbox
                      v-on="on"
                      v-model="props.selected"
                      hide-details
                      color="primary"
                    ></v-checkbox>
                  </td>
                  <td>{{ props.item.hostname }}</td>
                  <td>
                    <p
                      :key="index"
                      v-for="(env, index) of props.item.cmdsegments.envs"
                    >{{ env.name }}{{ env.value }}</p>
                  </td>
                  <td>{{ props.item.command }}</td>
                  <td>
                    <p
                      :key="index"
                      v-for="(param, index) of props.item.cmdsegments.params"
                    >{{ param.name }}{{ param.value }}</p>
                  </td>
                </tr>
              </template>
            </v-data-table>
          </v-flex>
        </v-layout>
      </v-card-text>
      <v-card-text>
        <v-layout align-center justify-end>
          <v-btn
            color="primary"
            @click="goToCreateTasks()"
            small
          >Go to tasks creator</v-btn>
        </v-layout>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>

<script>
import { getTasks } from '../../../../../api/tasks'
export default {
  name: 'TaskTemplateChooser',
  props: {
    showModal: {
      type: Boolean,
      default: false
    }
  },
  data () {
    return {
      existingTasks: [],
      selectedTasks: [],
      headers: [
        { text: 'Hostname', value: 'hostname' },
        { text: 'Environmental variables', value: 'cmdsegments' },
        { text: 'Command', value: 'command' },
        { text: 'Parameters', value: 'cmdsegments' }
      ],
      pagination: {
        sortBy: 'hostname',
        descending: false,
        rowsPerPage: 10
      }
    }
  },
  watch: {
    showModal () {
      getTasks(this.$store.state.accessToken)
        .then(tasks => {
          this.existingTasks = tasks
        })
        .catch(error => {
          this.$emit('error', error)
        })
    }
  },
  methods: {
    close: function () {
      this.$emit('close')
    },
    goToCreateTasks: function () {
      this.close()
      this.$emit('openFromExisting', this.selectedTasks)
    }
  }
}
</script>

<style scoped>
  .float-right-button {
    float: right;
  }
</style>
