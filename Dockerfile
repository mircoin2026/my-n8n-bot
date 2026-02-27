FROM n8nio/n8n:latest

# Переключаемся на пользователя root, чтобы исправить права
USER root
RUN mkdir -p /home/node/.n8n && chown -R node:node /home/node/.n8n

# Возвращаемся к пользователю node
USER node
