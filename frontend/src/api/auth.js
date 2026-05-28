import request from "@/utils/request";
import config from "@/config";

export default {
  /**
   * 发送验证码
   * @param {string} phone - 手机号
   * @param {string} type - 验证码类型: login/register/reset_password
   */
  sendCode(phone, type) {
    return request.post(config.api.auth.sendCode, {
      phone,
      type,
    });
  },

  /**
   * 登录
   * @param {Object} data
   * @param {string} data.phone - 手机号
   * @param {string} [data.password] - 密码(密码登录时必填)
   * @param {string} [data.code] - 验证码(验证码登录时必填)
   */
  login(data) {
    return request.post(config.api.auth.login, data);
  },

  /**
   * 注册
   * @param {Object} data
   * @param {string} data.phone - 手机号
   * @param {string} data.password - 密码
   * @param {string} data.code - 验证码
   * @param {string[]} data.usage_purposes - 使用目的
   */
  register(data) {
    return request.post(config.api.auth.register, data);
  },

  /**
   * 重置密码
   * @param {Object} data
   * @param {string} data.phone - 手机号
   * @param {string} data.password - 新密码
   * @param {string} data.code - 验证码
   */
  resetPassword(data) {
    return request.post(config.api.auth.resetPassword, data);
  },

  /**
   * 更新使用目的
   * @param {string[]} purposes - 新的使用目的列表
   */
  updatePurposes(purposes) {
    return request.post(config.api.auth.updatePurposes, {
      purposes,
    });
  },

  /**
   * 获取当前用户信息
   * @returns {Promise} 用户信息
   */
  getCurrentUser() {
    return request({
      url: "/auth/me",
      method: "get",
    });
  },

  /**
   * 设置用户为管理员
   * @param {string} phone - 目标用户手机号
   * @param {boolean} isAdmin - 是否设置为管理员
   * @returns {Promise} 设置结果
   */
  setAdmin(phone, isAdmin) {
    return request({
      url: "/api/auth/set-admin",
      method: "post",
      data: { phone, is_admin: isAdmin },
    });
  },
};
