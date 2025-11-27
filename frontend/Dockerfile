# Usamos una imagen de Node.js ligera
FROM node:22-alpine

# Directorio de trabajo
WORKDIR /app

# Copiamos los archivos de dependencias primero (para aprovechar caché)
COPY package.json package-lock.json ./

# Instalamos las dependencias
RUN npm install

# Copiamos el resto del código
COPY . .

# Exponemos el puerto de desarrollo de Angular
EXPOSE 4200

# Comando para iniciar en modo desarrollo (host 0.0.0.0 es vital para Docker)
CMD ["npm", "start", "--", "--host", "0.0.0.0", "--poll", "2000"]