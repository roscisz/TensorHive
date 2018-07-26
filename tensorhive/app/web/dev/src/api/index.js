import axios from 'axios'
import config from '../config'

export default {
  request (method, uri, data = null) {
    if (!method) {
      console.error('API function call requires method argument')
      return
    }

    if (!uri) {
      console.error('API function call requires uri argument')
      return
    }

    var url = config.serverURI + uri

    if (method === 'get' && uri === '/reservations') {
      return url
    }
    if (uri === '/machines') {
      return 6
    }
    return axios({ method, url, data })
  }
}
