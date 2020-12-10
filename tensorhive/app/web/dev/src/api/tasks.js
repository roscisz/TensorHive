import api from './index'

const tasksUrl = '/tasks'

export function getTask (token, taskId) {
  return api
    .request('get', `${tasksUrl}/${taskId}`, token)
    .then(response => response.data.task)
}

export function getTasks (token, jobId = null, syncAll = false) {
  return api
    .request('get', api.withQueryParams(tasksUrl, { jobId, syncAll }), token)
    .then(response => response.data.tasks)
}

export function getTaskLogs (token, taskId, tail = false) {
  return api
    .request(
      'get',
      api.withQueryParams(`${tasksUrl}/${taskId}/log`, { tail }),
      token
    )
    .then(response => ({
      path: response.data.path,
      lines: response.data.output_lines
    }))
}

export function updateTask (token, taskId, task) {
  return api
    .request('put', `${tasksUrl}/${taskId}`, token, task)
    .then(response => response.data.task)
}

export function deleteTask (token, taskId) {
  return api.request('delete', `${tasksUrl}/${taskId}`, token)
}
