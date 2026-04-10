FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
# Serve the static HTML from public/ and the compiled JS from dist/
COPY --from=build /app/public /usr/share/nginx/html
COPY --from=build /app/dist /usr/share/nginx/html/dist
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
