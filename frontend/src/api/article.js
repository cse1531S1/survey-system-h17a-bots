import fetch from '@/utils/fetch'

export function fetchList(query) {
  return fetch({
    url: 'http://127.0.0.1:9528/api/v1.0/fetch_all_survey',
    method: 'get',
    params: query
  })
}

export function fetchPool(query) {
  return fetch({
    url: 'http://127.0.0.1:9528/api/v1.0/question_pool',
    method: 'get',
    params: query
  })
}

export function fetchSRstatic() {
  return fetch({
    url: 'http://127.0.0.1:9528/api/v1.0/srstatic',
    method: 'get'
  })
}

export function fetchCourse(query) {
  return fetch({
    url: 'http://127.0.0.1:9528/api/v1.0/fetch_course',
    method: 'get'
  })
}

export function fetchQuestion() {
  return fetch({
    url: 'http://127.0.0.1:9528/api/v1.0/fetch_question',
    method: 'get'
  })
}

export function modifyUser(to_post) {
  return fetch({
    url: 'http://127.0.0.1:9528/api/v1.0/user_verify',
    method: 'post',
    data: to_post
  })
}
export function modifySurvey(to_post) {
  return fetch({
    url: 'http://127.0.0.1:9528/api/v1.0/modify_survey',
    method: 'post',
    data: to_post
  })
}

export function fetchUnverified(to_post) {
  return fetch({
    url: 'http://127.0.0.1:9528/api/v1.0/user_pool',
    method: 'post',
    params: to_post
  })
}

export function createSurvey(to_post) {
  return fetch({
    url: 'http://127.0.0.1:9528/api/v1.0/create_survey',
    method: 'post',
    data: to_post
  })
}

export function createQuestion(to_post) {
  return fetch({
    url: 'http://127.0.0.1:9528/api/v1.0/create_question',
    method: 'post',
    data: to_post
  })
}

export function loadUsers() {
  return fetch({
    url: 'http://127.0.0.1:9528/api/v1.0/load_user',
    method: 'get'
  })
}

export function fetchPie(surveyId, questionId) {
  var to_post = {
    survey: surveyId,
    question: questionId
  }
  return fetch({
    url: 'http://127.0.0.1:9528/api/v1.0/fetch_piechart',
    method: 'post',
    data: to_post
  })
}

export function fetchAnswers(query, id) {
  return fetch({
    url: 'http://127.0.0.1:9528/api/v1.0/fetch_answer',
    method: 'post',
    data: {
      id: id
    },
    params: query
  })
}

export function deleteQuestion(id) {
  var to_post = {
    id: id
  }
  return fetch({
    url: 'http://127.0.0.1:9528/api/v1.0/delete_question',
    method: 'post',
    data: to_post
  })
}
