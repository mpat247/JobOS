# Use official Node.js image
FROM node:18

# Set working directory in the container
WORKDIR /app

# Copy only package files first for better caching
COPY package.json package-lock.json ./

# Install dependencies
RUN npm install

# Copy the rest of the application
COPY . .

# Build the Next.js app (creates .next/ folder)
RUN npm run build

# Expose port for the production server
EXPOSE 3000

# Run Next.js in production mode
CMD ["npm", "run", "start"]
