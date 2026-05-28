import request from '@/utils/request'

// 角色列表参数接口
interface RolesParams {
  category?: string
  keyword?: string
  page?: number
  size?: number
}

// 图标接口
export interface RoleIcon {
  type: 'web' | 'video' | 'image' | 'pdf' | 'ppt' | 'default'
  icon: string
}

// 角色对象接口
export interface Role {
  id: number
  icon: string  // 保留向后兼容
  icons?: RoleIcon[]  // 新的多图标字段
  title: string
  description: string
  tags: string[]
  rating: number
  serviceCount: number
  category: string
  sub_category?: string
}

// 角色详情接口
export interface RoleDetail extends Role {
  capabilities: string[]
  examples: string[]
  prompt: string
}

// 获取角色列表
export function getRoles(params?: RolesParams) {
  return request<{
    roles: Role[]
    total: number
  }>({
    url: '/api/roles',
    method: 'get',
    params
  })
}

// 获取角色详情
export function getRoleDetail(roleId: number) {
  return request<{
    role: RoleDetail
  }>({
    url: `/api/roles/${roleId}`,
    method: 'get'
  })
} 