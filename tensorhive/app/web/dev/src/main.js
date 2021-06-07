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

import axios from 'axios'
import config from './config'

axios.get('/static/config.json').then(response => {
  config.serverURI = response.data.apiPath
  config.version = response.data.version
  if (window.localStorage) {
    var version = JSON.parse(window.localStorage.getItem('version'))
    if (version === null) {
      if (config.version !== undefined) {
        window.localStorage.setItem('version', JSON.stringify(config.version))
      } else {
        window.localStorage.setItem('version', JSON.stringify('no data in config file'))
      }
    } else if (version !== config.version) {
      window.localStorage.clear()
      location.reload(true)
    }
  }

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

  axios.interceptors.response.use(null, (error) => {
    if (error.config.url === config.serverURI + '/user/refresh') {
      if (window.localStorage) {
        window.localStorage.setItem('user', null)
        window.localStorage.setItem('role', null)
        window.localStorage.setItem('accessToken', null)
        window.localStorage.setItem('refreshToken', null)
      }
      store.commit('SET_USER', null)
      store.commit('SET_ROLE', null)
      store.commit('SET_ACCESS_TOKEN', null)
      store.commit('SET_REFRESH_TOKEN', null)
      router.push('/login')
    } else {
      if (error.config && error.response && error.response.status === 401 && error.config.url !== config.serverURI + '/user/login') {
        axios.defaults.headers.common['Authorization'] = store.state.refreshToken
        return axios({ method: 'get', url: config.serverURI + '/user/refresh', data: null })
          .then(response => {
            store.commit('SET_ACCESS_TOKEN', 'Bearer ' + response.data.access_token)
            if (window.localStorage) {
              window.localStorage.setItem('accessToken', 'Bearer ' + response.data.access_token)
            }
            error.config.headers['Authorization'] = 'Bearer ' + response.data.access_token
            return axios.request(error.config)
          })
          .catch(error => {
            handleError(error)
            logout()
          })
      }
    }
    return Promise.reject(error)
  })
  // Check local storage to handle refreshes
  if (window.localStorage) {
    var localUserString = window.localStorage.getItem('user') || 'null'
    var localUser = JSON.parse(localUserString)

    if (localUser && store.state.user !== localUser) {
      store.commit('SET_USER', localUser)
      store.commit('SET_ACCESS_TOKEN', window.localStorage.getItem('accessToken'))
      store.commit('SET_REFRESH_TOKEN', window.localStorage.getItem('refreshToken'))
      store.commit('SET_ROLE', window.localStorage.getItem('role'))
      store.commit('SET_ID', parseInt(window.localStorage.getItem('userId')))
    }
  }
  function handleError (error) {
    if (!error.hasOwnProperty('response')) {
      console.log(error.message)
    } else {
      if (!error.response.data.hasOwnProperty('msg')) {
        console.log(error.response.data)
      } else {
        console.log(error.response.data.msg)
      }
    }
  }

  function logout () {
    if (store.state.accessToken !== null) {
      api
        .request('delete', '/user/logout', store.state.accessToken)
        .then(response => {
          store.commit('SET_ACCESS_TOKEN', null)
          if (window.localStorage) {
            window.localStorage.setItem('accessToken', null)
          }
          if (store.state.refreshToken !== null) {
            api
              .request('delete', '/user/logout/refresh_token', store.state.refreshToken)
              .then(response => {
                store.commit('SET_REFRESH_TOKEN', null)
                if (window.localStorage) {
                  window.localStorage.setItem('refreshToken', null)
                }
              })
              .catch(error => {
                handleError(error)
              })
          }
        })
        .catch(error => {
          this.handleError(error)
        })
    }
    store.commit('SET_USER', null)
    store.commit('SET_ROLE', null)

    if (window.localStorage) {
      window.localStorage.setItem('user', null)
      window.localStorage.setItem('role', null)
    }
    router.push('/login')
  }
  // Start out app!
  // eslint-disable-next-line no-new
  new Vue({
    el: '#root',
    router: router,
    store: store,
    render: h => h(AppView)
  })
})
