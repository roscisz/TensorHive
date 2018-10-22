export default {
  TOGGLE_LOADING (state) {
    state.callingAPI = !state.callingAPI
  },
  TOGGLE_SEARCHING (state) {
    state.searching = (state.searching === '') ? 'loading' : ''
  },
  SET_USER (state, user) {
    state.user = user
  },
  SET_ROLE (state, role) {
    state.role = role
  },
  SET_ID (state, id) {
    state.id = id
  },
  SET_ACCESS_TOKEN (state, token) {
    state.accessToken = token
  },
  SET_REFRESH_TOKEN (state, token) {
    state.refreshToken = token
  }
}
