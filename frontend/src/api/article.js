import fetch from '@/utils/fetch'

export function fetchList(query) {
  return fetch({
    url: 'http://127.0.0.1:5000/api/v1.0/fetch_all_survey',
    method: 'get',
    params: query
  })
}

export function fetchPool(query) {
  return fetch({
    url: 'http://127.0.0.1:5000/api/v1.0/question_pool',
    method: 'get',
    params: query
  })
}

export function fetchCourse(query) {
  return fetch({
    url: 'http://127.0.0.1:5000/api/v1.0/fetch_course',
    method: 'get'
  })
}

export function fetchArticle() {
  return fetch({
    url: '/article/detail',
    method: 'get'
  })
}

export function fetchQuestion() {
  return fetch({
    url: 'http://127.0.0.1:5000/api/v1.0/fetch_question',
    method: 'get'
  })
}

export function fetchPv(pv) {
  return fetch({
    url: '/article/pv',
    method: 'get',
    params: {
      pv
    }
  })
}

export function modifySurvey(to_post) {
  return fetch({
    url: 'http://127.0.0.1:5000/api/v1.0/modify_survey',
    method: 'post',
    data: to_post
  })
}

export function createSurvey(to_post) {
  return fetch({
    url: 'http://127.0.0.1:5000/api/v1.0/create_survey',
    method: 'post',
    data: to_post
  })
}

export function createQuestion(to_post) {
  return fetch({
    url: 'http://127.0.0.1:5000/api/v1.0/create_question',
    method: 'post',
    data: to_post
  })
}
