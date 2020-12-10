<template>
  <v-list v-if="envs.length > 0">
    <v-list-tile v-for="env in envs" :key="env.id">
      <v-list-tile-action>
        <v-tooltip bottom>
          <template v-slot:activator="{ on }">
            <v-icon v-on="on">tune</v-icon>
          </template>
          <span>Environment variable</span>
        </v-tooltip>
      </v-list-tile-action>

      <v-list-tile-content>
        <v-list-tile-title class="text-monospace">
          <span>{{ env.name }}={{ env.value }}</span>
        </v-list-tile-title>
      </v-list-tile-content>

      <v-list-tile-action>
        <v-tooltip bottom>
          <template v-slot:activator="{ on }">
            <v-btn
              v-on="on"
              flat
              icon
              color="grey"
              @click="$emit('remove', env.id)"
            >
              <v-icon>delete</v-icon>
            </v-btn>
          </template>
          <span>Remove this variable</span>
        </v-tooltip>
      </v-list-tile-action>
    </v-list-tile>
  </v-list>
  <span class="body-1 px-3" v-else>{{ noDataText }}</span>
</template>

<script>
export default {
  props: {
    noDataText: {
      type: String,
      default: 'No environment variables specified'
    },
    envs: {
      type: Array,
      required: true
    }
  }
}
</script>

<style scoped>
.text-monospace {
  font-family: ui-monospace, "SF Mono", SFMono-Regular, "DejaVu Sans Mono",
    Liberation Mono, Menlo, Consolas, Monaco, monospace;
}
</style>
