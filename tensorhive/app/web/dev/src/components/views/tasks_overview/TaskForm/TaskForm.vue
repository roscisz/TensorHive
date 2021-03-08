<template>
  <div class="allow-flex-shrink">
    <v-card flat>
      <v-card-title v-if="header" primary-title>
        <h5 class="headline">{{ header }}</h5>
      </v-card-title>

      <template v-if="!loading && !error">
        <v-card-text style="height: 60%;">
          <v-container class="pa-0">
            <v-layout>
              <v-flex xs12>
                <v-subheader>Basic information</v-subheader>
                <TaskFormBasicInfo
                  ref="basicInfo"
                  :hosts="hosts"
                  :hostname.sync="internalHostname"
                  :resource.sync="internalResource"
                  :command.sync="internalCommand"
                />
              </v-flex>
            </v-layout>

            <v-layout class="mb-5" wrap>
              <v-flex xs12 md6>
                <v-subheader>Environment variables</v-subheader>
                <TaskFormEnvs :envs="envs" @remove="removeEnv" />
              </v-flex>

              <v-flex xs12 md6>
                <v-subheader>Parameters</v-subheader>
                <TaskFormParams :params="params" @remove="removeParam" />
              </v-flex>
            </v-layout>

            <v-layout class="mb-4">
              <v-flex xs12>
                <v-subheader>Add a variable or a parameter</v-subheader>
                <TaskFormExtras
                  ref="extras"
                  @addEnv="addEnv"
                  @addParam="addParam"
                />
              </v-flex>
            </v-layout>
            <v-layout v-if="tfConfigVisible">
              <v-flex xs12>
                <v-subheader>TF CONFIG
                  <v-switch
                    class="float-right-button"
                    v-if="chosenTemplate === 'tf2'"
                    v-model="enableSmartTfConfig"
                    label="Smart TF_CONFIG"
                  />
                </v-subheader>
              </v-flex>
            </v-layout>
            <v-layout class="mb-3">
              <v-flex xs12>
                <v-subheader>Full command</v-subheader>
                <div class="command-field">
                  <TaskCommand
                    no-command-text="Fill in the form to see how your command will look like"
                    :command="stringifiedCommand"
                  />
                </div>
              </v-flex>
            </v-layout>
          </v-container>
        </v-card-text>

        <v-card-actions>
          <v-btn
            v-if="cancelButton"
            flat
            color="primary"
            @click="$emit('cancel')"
          >
            Cancel
          </v-btn>
          <v-spacer></v-spacer>
          <v-btn v-if="clearButton" flat color="primary" @click="reset">
            Clear
          </v-btn>
          <v-btn color="primary" @click="submit">
            Submit
          </v-btn>
        </v-card-actions>
      </template>

      <template v-else>
        <v-card-text>
          <v-container>
            <v-layout align-center justify-center>
              <v-progress-circular
                v-if="loading"
                indeterminate
                color="primary"
                :size="64"
              ></v-progress-circular>
              <v-alert :value="true" color="error" icon="warning" outline>
                <p class="body-2">
                  An error occured while fetching nodes metrics
                </p>
                <p class="body-1">{{ errorMessage }}</p>
              </v-alert>
            </v-layout>
          </v-container>
        </v-card-text>

        <v-card-actions>
          <v-btn
            v-if="cancelButton"
            flat
            color="primary"
            @click="$emit('cancel')"
          >
            Cancel
          </v-btn>
          <v-spacer></v-spacer>
        </v-card-actions>
      </template>
    </v-card>
  </div>
</template>

<script>
import api from '../../../../api'
import { getErrorMessage } from '../../../../utils/errors'
import TaskFormBasicInfo from './TaskFormBasicInfo'
import TaskFormEnvs from './TaskFormEnvs'
import TaskFormParams from './TaskFormParams'
import TaskFormExtras from './TaskFormExtras'
import TaskCommand, { stringifyCommand } from '../TaskCommand'

export default {
  components: {
    TaskFormBasicInfo,
    TaskFormEnvs,
    TaskFormParams,
    TaskFormExtras,
    TaskCommand
  },
  props: {
    cancelButton: {
      type: Boolean,
      default: true
    },
    clearButton: {
      type: Boolean,
      default: true
    },
    header: String,
    hostname: String,
    resource: Object,
    command: String
  },
  data () {
    return {
      internalHostname: this.hostname,
      internalResource: this.resource,
      internalCommand: this.command,
      envs: [],
      envId: 0,
      params: [],
      paramId: 0,
      hosts: {},
      loading: false,
      error: undefined
    }
  },
  computed: {
    errorMessage () {
      return getErrorMessage(this.error)
    },
    stringifiedCommand () {
      if (
        !!this.internalHostname &&
        !!this.internalResource &&
        !!this.internalCommand
      ) {
        return stringifyCommand(
          this.internalHostname,
          this.internalResource,
          this.internalCommand,
          this.envs,
          this.params
        )
      }
    }
  },
  mounted () {
    // TODO: handle errors
    api
      .request('get', '/nodes/metrics', this.$store.state.accessToken)
      .then(response => {
        this.hosts = {}

        for (const [hostname, host] of Object.entries(response.data)) {
          const gpus = Object.values(host.GPU || {}).map(({ index }) => ({
            name: `GPU${index}`,
            id: index
          }))

          this.hosts[hostname] = [{ name: 'CPU', id: null }, ...gpus]
        }
      })
  },
  methods: {
    addEnv (name, value = '') {
      this.envs.push({ id: this.envId++, name, value })
    },
    removeEnv (id) {
      this.envs = this.envs.filter(env => env.id !== id)
    },
    addParam (name, value = '') {
      this.params.push({ id: this.paramId++, name, value })
    },
    removeParam (id) {
      this.params = this.params.filter(param => param.id !== id)
    },
    reset () {
      this.envs = []
      this.envId = 0
      this.params = []
      this.paramId = 0

      this.$refs.basicInfo.reset()
      this.$refs.extras.reset()
    },
    submit () {
      if (this.$refs.basicInfo.validate()) {
        const task = {
          hostname: this.internalHostname,
          cmdsegments: {
            envs: this.envs,
            params: this.params
          }
        }

        if (this.internalResource !== undefined && this.internalResource !== null) {
          if (this.internalResource.id === undefined || this.internalResource.id === null) {
            task.command = 'CUDA_VISIBLE_DEVICES= ' + this.internalCommand
          } else {
            task.command = `CUDA_VISIBLE_DEVICES=${String(this.internalResource.id)} ` + this.internalCommand
          }
        }
        this.reset()
        this.$emit('submit', task)
      }
    }
  }
}
</script>

<style scoped>
/* This resets font weight set by Bootstrap to the default 'normal' value. */
/* The proper way of creating a deep selector would be using `::v-deep` but */
/* it requires Vue Loader v15 which we do not use for now. */
label {
  font-weight: normal;
}

.command-field {
  margin: 0 16px;
  border-radius: 4px;
  padding: 0 16px;
  background-color: rgba(0, 0, 0, 0.06);
}

.allow-flex-shrink {
  /* By default flexbox items cannot shrink past the size of theirs content. */
  /* Changing their `min-width` to 0 allows them to do that and make it */
  /* possible to display the task command with horizontal scroll. */
  min-width: 0;
}
</style>
