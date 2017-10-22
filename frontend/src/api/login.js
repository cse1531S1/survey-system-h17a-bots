import fetch from '@/utils/fetch'

export function loginByUsername(username, password) {
  const data = {
    username,
    password
  }
  return fetch({
    url: 'http://127.0.0.1:9528/api/v1.0/get_token',
    method: 'post',
    data: data,
    auth: {
      username: username,
      password: password
    }
  })
}

export function register(data) {
  return fetch({
    url: 'http://127.0.0.1:9528/api/v1.0/register',
    method: 'post',
    data: data
  })
}

export function logout() {
  return fetch({
    url: 'http://127.0.0.1:9528/api/v1.0/logoff',
    method: 'post'
  })
}

export function getUserInfo(token) {
  return fetch({
    url: 'http://127.0.0.1:9528/api/v1.0/get_info',
    method: 'get'
    // params: { token }
  })
}
