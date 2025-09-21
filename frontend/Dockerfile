# Stage 1: Build the frontend application
# We use Node.js 18 with Alpine for a lean build environment
FROM node:18-alpine AS build

# Set the working directory
WORKDIR /app

# Copy package.json and package-lock.json and install dependencies
# This is done first to cache the npm install layer
COPY package*.json ./
RUN npm install

# Copy the rest of the application code
COPY . .

# Build the frontend for production
RUN npm run build

# Stage 2: Serve the static files with Nginx
# Nginx is a very fast and small web server
FROM nginx:alpine

# Copy the build output from the 'build' stage into Nginx's web root
COPY --from=build /app/dist /usr/share/nginx/html

# Expose port 80 for standard HTTP traffic
EXPOSE 80

# The command to start Nginx
CMD ["nginx", "-g", "daemon off;"]
