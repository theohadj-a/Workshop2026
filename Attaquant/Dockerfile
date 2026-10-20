# Utilisation d'une image Node.js officielle légère
FROM node:20-alpine

# Définition du répertoire de travail dans le conteneur
WORKDIR /app

# Copie des fichiers de dépendances
COPY package*.json ./

# Installation des dépendances (utilisation de npm install pour le mode dev)
RUN npm install --legacy-peer-deps

# Copie du reste du code source de l'application
COPY . .

# Exposition du port par défaut de Next.js
EXPOSE 3001

# Commande pour lancer le serveur de développement en écoutant sur toutes les interfaces (0.0.0.0)
CMD ["npm", "run", "dev", "--", "-H", "0.0.0.0"]