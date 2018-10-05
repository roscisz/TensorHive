import axios from 'axios'
import config from '../config'

export default {
  request (method, uri, token, data = null) {
    if (!method) {
      console.error('API function call requires method argument')
      return
    }

    if (!uri) {
      console.error('API function call requires uri argument')
      return
    }

    var url = config.serverURI + uri
    if (token !== null) {
      axios.defaults.headers.common['Authorization'] = token
    }

    return axios({ method: method, url: url, data: data })
  }
}
