FROM node:22-alpine

WORKDIR /app

COPY package.json ./
RUN npm install --omit=dev --no-audit --no-fund

COPY express.js ./

EXPOSE 4567

CMD ["npm", "start"]
