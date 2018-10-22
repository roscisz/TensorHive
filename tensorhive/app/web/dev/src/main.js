// Import ES6 Promise
import 'es6-promise/auto'

// Import System requirements
import Vue from 'vue'
import VueRouter from 'vue-router'

import { sync } from 'vuex-router-sync'
import routes from './routes'
import store from './store'
import api from './api'

// Import Helpers for filters
import { domain, count, prettyDate, pluralize } from './filters'

// Import Views - Top level
import AppView from './components/App.vue'

import Vuetify from 'vuetify'
import 'vuetify/dist/vuetify.min.css'
import 'material-design-icons-iconfont/dist/material-design-icons.css'

import staticConfig from '../static/config'
import config from './config'

config.serverURI = staticConfig.apiPath

Vue.use(Vuetify)

// Import Install and register helper items
Vue.filter('count', count)
Vue.filter('domain', domain)
Vue.filter('prettyDate', prettyDate)
Vue.filter('pluralize', pluralize)

Vue.use(VueRouter)

// Routing logic
var router = new VueRouter({
  routes: routes,
  mode: 'history',
  linkExactActiveClass: 'active',
  scrollBehavior: function (to, from, savedPosition) {
    return savedPosition || { x: 0, y: 0 }
  }
})

// Some middleware to help us ensure the user is authenticated.
router.beforeEach((to, from, next) => {
  if (
    to.matched.some(record => record.meta.requiresAuth) &&
    (!router.app.$store.state.accessToken || router.app.$store.state.accessToken === 'null')
  ) {
    // this route requires auth, check if logged in
    // if not, redirect to login page.
    window.console.log('Not authenticated')
    next({
      path: '/login',
      query: { redirect: to.fullPath }
    })
  } else if (to.meta.role === 'admin') {
    if (router.app.$store.state.role === 'admin') {
      next()
    } else {
      next({
        path: '/',
        query: { redirect: to.fullPath }
      })
    }
  } else {
    next()
  }
})

sync(store, router)

// Check local storage to handle refreshes
if (window.localStorage) {
  var localUserString = window.localStorage.getItem('user') || 'null'
  var localUser = JSON.parse(localUserString)

  if (localUser && store.state.user !== localUser) {
    store.commit('SET_USER', localUser)
    store.commit('SET_ACCESS_TOKEN', window.localStorage.getItem('accessToken'))
    store.commit('SET_REFRESH_TOKEN', window.localStorage.getItem('refreshToken'))
    store.commit('SET_ROLE', window.localStorage.getItem('role'))
    store.commit('SET_ID', window.localStorage.getItem('userId'))
  }
  refreshToken()
}

function refreshToken () {
  api
    .request('get', '/user/refresh', store.state.refreshToken)
    .then(response => {
      store.commit('SET_ACCESS_TOKEN', 'Bearer ' + response.data.access_token)
      if (window.localStorage) {
        window.localStorage.setItem('accessToken', 'Bearer ' + response.data.access_token)
      }
      window.setTimeout(function () {
        refreshToken()
      }, 55000)
    })
}

// Start out app!
// eslint-disable-next-line no-new
new Vue({
  el: '#root',
  router: router,
  store: store,
  render: h => h(AppView)
})
