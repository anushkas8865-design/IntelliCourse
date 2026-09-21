import { apiRequest } from './api'

export async function registerUser(name, email, password) {
  return apiRequest('/api/auth/register', {
    method: 'POST',
    body: JSON.stringify({
      name,
      email,
      password,
    }),
  })
}

export async function loginUser(email, password) {
  return apiRequest('/api/auth/login', {
    method: 'POST',
    body: JSON.stringify({
      email,
      password,
    }),
  })
}

export async function getProfile(token) {
  return apiRequest('/api/auth/profile', {
    method: 'GET',
    headers: {
      Authorization: `Bearer ${token}`,
    },
  })
}

export async function updateProfile(token, data) {
  return apiRequest('/api/auth/profile', {
    method: 'PUT',
    headers: {
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(data),
  })
}