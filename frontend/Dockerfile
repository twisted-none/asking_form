# Многоэтапная сборка для React приложения

# Этап 1: Сборка
FROM node:18-alpine as build

WORKDIR /app

# Копируем ВСЕ файлы фронтенда
COPY frontend/ ./

# Устанавливаем зависимости
RUN npm install

# Собираем приложение
RUN npm run build

# Этап 2: Production сервер
FROM nginx:alpine

# Копируем собранное приложение
COPY --from=build /app/dist /usr/share/nginx/html

# Копируем конфигурацию nginx
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf

# Открываем порт
EXPOSE 80

# Запускаем nginx
CMD ["nginx", "-g", "daemon off;"]