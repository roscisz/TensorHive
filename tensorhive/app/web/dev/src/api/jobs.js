import api from './index'

const jobsUrl = '/jobs'

export function getJob (token, jobId) {
  return api
    .request('get', `${jobsUrl}/${jobId}`, token)
    .then(response => response.data.job)
}

export function getJobs (token, userId = null) {
  return api
    .request('get', api.withQueryParams(jobsUrl, { userId }), token)
    .then(response => response.data.jobs)
}

export function createJob (token, job) {
  return api
    .request('post', jobsUrl, token, job)
    .then(response => response.data.job)
}

// TODO: This should probably be located under `/tasks` not `/jobs`.
export function createJobTask (token, jobId, task) {
  return api
    .request('post', `${jobsUrl}/${jobId}/tasks`, token, task)
    .then(response => response.data.task)
}

export function updateJob (token, jobId, job) {
  return api
    .request('put', `${jobsUrl}/${jobId}`, token, job)
    .then(response => response.data.job)
}

export function enqueueJob (token, jobId) {
  return api
    .request('put', `${jobsUrl}/${jobId}/enqueue`, token)
    .then(response => response.data.job)
}

export function dequeueJob (token, jobId) {
  return api
    .request('put', `${jobsUrl}/${jobId}/dequeue`, token)
    .then(response => response.data.job)
}

export function deleteJob (token, jobId) {
  return api.request('delete', `${jobsUrl}/${jobId}`, token)
}

export function executeJob (token, jobId) {
  return api
    .request('get', `${jobsUrl}/${jobId}/execute`, token)
    .then(response => response.data.job)
}

export function stopJob (token, jobId, gracefully = null) {
  return api
    .request(
      'get',
      api.withQueryParams(`${jobsUrl}/${jobId}/stop`, { gracefully }),
      token
    )
    .then(response => response.data.job)
}

export function killJob (token, jobId) {
  return stopJob(token, jobId, false)
}

export function addTaskToJob (token, jobId, taskId) {
  return api.request('put', `${jobsUrl}/${jobId}/tasks/${taskId}`, token)
}

export function deleteTaskFromJob (token, jobId, taskId) {
  return api.request('delete', `${jobsUrl}/${jobId}/tasks/${taskId}`, token)
}
