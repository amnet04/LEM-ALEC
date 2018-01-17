# Create image based on the official Node 6 image from dockerhub
FROM node:6

WORKDIR /src/

RUN npm install
CMD ["npm", "start"]