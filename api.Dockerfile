FROM node:latest

WORKDIR /api

COPY api/package.json ./
RUN npm install

COPY api/ .

RUN npm run compile

CMD [ "node", "api.js" ]