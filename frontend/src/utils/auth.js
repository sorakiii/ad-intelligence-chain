// 从本地存储获取令牌
export const getToken = () => {
  return localStorage.getItem('token') || ''
}

// 设置令牌到本地存储
export const setToken = (token) => {
  localStorage.setItem('token', token)
}

// 移除令牌
export const removeToken = () => {
  localStorage.removeItem('token')
} 