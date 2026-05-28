#!/usr/bin/env node

/**
 * 自动更新版本号的脚本
 * 用于在构建时自动更新版本信息，确保缓存失效
 */

const fs = require('fs');
const path = require('path');

/**
 * 获取当前时间戳
 * @returns {string} 格式化的时间戳
 */
function getCurrentTimestamp() {
  const now = new Date();
  return now.toISOString();
}

/**
 * 生成版本号（基于时间戳）
 * @returns {string} 版本号
 */
function generateVersion() {
  // 优先使用环境变量中的版本号（Docker构建时传入）
  if (process.env.BUILD_VERSION) {
    return process.env.BUILD_VERSION;
  }
  
  const now = new Date();
  const year = now.getFullYear();
  const month = String(now.getMonth() + 1).padStart(2, '0');
  const day = String(now.getDate()).padStart(2, '0');
  const hour = String(now.getHours()).padStart(2, '0');
  const minute = String(now.getMinutes()).padStart(2, '0');
  
  return `${year}.${month}.${day}.${hour}${minute}`;
}

/**
 * 更新版本文件
 */
function updateVersionFiles() {
  const version = generateVersion();
  // 优先使用环境变量中的构建时间（Docker构建时传入）
  const buildTime = process.env.BUILD_DATE || getCurrentTimestamp();
  
  console.log(`🔄 更新版本号: ${version}`);
  console.log(`📅 构建时间: ${buildTime}`);
  
  // 更新 version.js
  const versionJsPath = path.join(__dirname, '../src/version.js');
  const versionJsContent = `export const APP_VERSION = '${version}';
export const BUILD_TIME = '${buildTime}';`;

  try {
    fs.writeFileSync(versionJsPath, versionJsContent, 'utf8');
    console.log('✅ 已更新 src/version.js');
  } catch (error) {
    console.error('❌ 更新 src/version.js 失败:', error.message);
  }
  
  // 更新 public/version.json
  const versionJsonPath = path.join(__dirname, '../public/version.json');
  const versionJsonContent = {
    version: version,
    build_date: buildTime,
    description: "AI广告平台前端应用"
  };

  try {
    fs.writeFileSync(versionJsonPath, JSON.stringify(versionJsonContent, null, 2), 'utf8');
    console.log('✅ 已更新 public/version.json');
  } catch (error) {
    console.error('❌ 更新 public/version.json 失败:', error.message);
  }
  
  // 更新 package.json 版本号
  const packageJsonPath = path.join(__dirname, '../package.json');
  try {
    const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));
    packageJson.version = version;
    fs.writeFileSync(packageJsonPath, JSON.stringify(packageJson, null, 2), 'utf8');
    console.log('✅ 已更新 package.json 版本号');
  } catch (error) {
    console.error('❌ 更新 package.json 失败:', error.message);
  }
  
  console.log('🎉 版本更新完成！');
}

// 如果直接运行此脚本
if (require.main === module) {
  updateVersionFiles();
}

module.exports = {
  updateVersionFiles,
  generateVersion,
  getCurrentTimestamp
};
