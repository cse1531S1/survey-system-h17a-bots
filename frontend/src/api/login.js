import fetch from '@/utils/fetch'

export function loginByUsername(username, password) {
  const data = {
    username,
    password
  }
  return fetch({
    url: 'http://127.0.0.1:5000/api/v1.0/get_token',
    method: 'post',
    data: data,
    auth: {
      username: username,
      password: password
    }
  })
}

export function logout() {
  return fetch({
    url: 'http://127.0.0.1:5000/api/v1.0/logoff',
    method: 'post'
  })
}

export function getUserInfo(token) {
  return fetch({
    url: 'http://127.0.0.1:5000/api/v1.0/get_info',
    method: 'get'
    // params: { token }
  })
}

