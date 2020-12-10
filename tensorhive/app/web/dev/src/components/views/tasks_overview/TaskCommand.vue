<template>
  <div class="command-wrapper py-3">
    <div class="command">
      <span class="text-monospace" v-if="command">{{ command }}</span>
      <span v-else>{{ noCommandText }}</span>
    </div>
  </div>
</template>

<script>
export function stringifyCommand (hostname, resource, command, envs, params) {
  const segments = []

  if (hostname !== undefined && hostname !== null) {
    segments.push(String(hostname))
  }

  if (resource !== undefined && resource !== null) {
    if (resource.id === undefined || resource.id === null) {
      segments.push('CUDA_VISIBLE_DEVICES=')
    } else {
      segments.push(`CUDA_VISIBLE_DEVICES=${String(resource.id)}`)
    }
  }

  if (Array.isArray(envs)) {
    segments.push(
      envs
        .map(({ name, value }) =>
          value === undefined || value === null
            ? `${name}=`
            : `${name}=${value}`
        )
        .join(' ')
    )
  }

  if (command !== undefined && command !== null) {
    segments.push(String(command))
  }

  if (Array.isArray(params)) {
    segments.push(
      params
        .map(({ name, value }) =>
          value === undefined || value === null ? name : `${name} ${value}`
        )
        .join(' ')
    )
  }

  return segments.join(' ')
}

export default {
  props: {
    command: String,
    noCommandText: {
      type: String,
      default: 'No command specified'
    }
  }
}
</script>

<style scoped>
.command-wrapper {
  overflow-x: auto;
  white-space: nowrap;
}

.command {
  /* Setting the `display` and the `right-margin` properties here to fix an */
  /* ignored parent padding. See also: */
  /* https://stackoverflow.com/questions/10054870/when-a-child-element-overflows-horizontally-why-is-the-right-padding-of-the-par */
  display: inline-block;
}
.text-monospace {
  font-family: ui-monospace, "SF Mono", SFMono-Regular, "DejaVu Sans Mono",
    Liberation Mono, Menlo, Consolas, Monaco, monospace;
}
</style>
