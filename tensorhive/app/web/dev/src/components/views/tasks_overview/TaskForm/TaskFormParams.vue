<template>
  <v-list v-if="params.length > 0">
    <v-list-tile v-for="param in params" :key="param.id">
      <v-list-tile-action>
        <v-tooltip bottom>
          <template v-slot:activator="{ on }">
            <v-icon v-on="on">input</v-icon>
          </template>
          <span>Parameter</span>
        </v-tooltip>
      </v-list-tile-action>

      <v-list-tile-content>
        <v-list-tile-title class="text-monospace">
          <span v-if="param.value !== undefined"
            >{{ param.name }}{{ param.value }}</span
          >
          <span v-else>{{ param.name }}</span>
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
              @click="$emit('remove', param.id)"
            >
              <v-icon>delete</v-icon>
            </v-btn>
          </template>
          <span>Remove this parameter</span>
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
      default: 'No parameters specified'
    },
    params: {
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
