function capitalize (str) {
  return str.charAt(0).toUpperCase() + str.slice(1)
}

export function required (inputName) {
  return v => !!v || `${capitalize(inputName)} is required`
}

export function maxLength (inputName, max) {
  return v =>
    (v || '').length <= max ||
    `${capitalize(inputName)} must have at most ${max} character${
      max === 1 ? '' : 's'
    }`
}

export function startsWith (inputName, str) {
  return v =>
    (v || '').startsWith(str) ||
    `${capitalize(inputName)} must start with '${str}'`
}
