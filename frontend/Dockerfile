# Многоэтапная сборка для React приложения

# Этап 1: Сборка
FROM node:18-alpine as build

WORKDIR /app

# Копируем package.json из frontend директории
COPY frontend/package*.json ./

# Устанавливаем зависимости
RUN npm install

# Копируем конфигурационные файлы из корня
COPY vite.config.ts ./
COPY tailwind.config.js ./
COPY postcss.config.js ./
COPY tsconfig*.json ./
COPY eslint.config.js ./
COPY index.html ./

# Копируем исходный код из frontend
COPY frontend/ ./frontend/

# Собираем приложение
RUN npm run build

# Этап 2: Production сервер
FROM nginx:alpine

# Копируем собранное приложение
COPY --from=build /app/dist /usr/share/nginx/html

# Копируем конфигурацию nginx из frontend директории
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf

# Открываем порт
EXPOSE 80

# Запускаем nginx
CMD ["nginx", "-g", "daemon off;"]