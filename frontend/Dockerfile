# Simple nginx image - expects pre-built dist folder
# Build locally first: cd frontend && npm install && npm run build
FROM nginx:alpine
COPY dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
