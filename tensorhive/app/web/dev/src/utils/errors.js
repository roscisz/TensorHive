export function getErrorMessage (error) {
  let message = ''

  if (typeof error === 'object' && error !== null) {
    if (error.response) {
      if (error.response.data && error.response.data.msg) {
        message = error.response.data.msg
      } else if (error.response.msg) {
        message = error.response.msg
      } else {
        message = `${error.response.request.responseURL} - ${error.response.status} ${error.response.statusText}`
      }
    } else if (error.request) {
      message = 'A request sent to the server did not receive any response'
    } else {
      message = error.message || error
    }
  } else {
    message = error
  }

  message = String(message)

  if (message === '') {
    message = '<empty error message>'
  }

  return message
}
