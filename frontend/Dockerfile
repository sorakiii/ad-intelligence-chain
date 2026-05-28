# 构建阶段
FROM node:20 as build

# 设置工作目录
WORKDIR /app

# 复制 package.json 和 package-lock.json
COPY package*.json ./

# 安装依赖
RUN npm install

# 复制源代码
COPY . .

# 接收构建参数
ARG VITE_API_URL
ARG BUILD_VERSION
ARG BUILD_DATE
ENV VITE_API_URL=$VITE_API_URL
ENV BUILD_VERSION=$BUILD_VERSION
ENV BUILD_DATE=$BUILD_DATE

# 构建应用 - 自动更新版本号
RUN npm run build

# 生产阶段
FROM nginx:alpine

# 从构建阶段复制构建文件
COPY --from=build /app/dist /usr/share/nginx/html

# 复制nginx配置
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 暴露端口
EXPOSE 80 443

# 启动nginx
CMD ["nginx", "-g", "daemon off;"] 