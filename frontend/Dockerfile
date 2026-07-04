FROM node:20-alpine
WORKDIR /app

# Install deps first (cached layer)
COPY package.json .
RUN npm install

# Copy source
COPY . .

EXPOSE 5173

# --host makes Vite listen on 0.0.0.0 so Docker can expose the port
CMD ["npm", "run", "dev"]
