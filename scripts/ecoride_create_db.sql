-- ############################################
-- SCHEMA DE LA BASE DE DONNEES POUR ECORIDE (version simplifiée)
-- ############################################

-- Types ENUM
CREATE TYPE opinion_status AS ENUM('pending', 'approved', 'rejected');
CREATE TYPE carpooling_status AS ENUM('draft', 'published', 'finished', 'cancelled');
CREATE TYPE energy AS ENUM('diesel', 'essence', 'electric', 'hybrid');

-- Table users
CREATE TABLE ecoride.users(
   id SERIAL PRIMARY KEY,
   username VARCHAR(50) NOT NULL UNIQUE,
   firstname VARCHAR(100),
   lastname VARCHAR(100),
   email VARCHAR(250) NOT NULL UNIQUE,
   password_hash VARCHAR(256) NOT NULL,
   phone VARCHAR(10),
   address VARCHAR(250),
   birth_date DATE,
   photo VARCHAR(255),
   credit DECIMAL(6, 2) DEFAULT 20,  -- 20 crédits par défaut
   created_at TIMESTAMPTZ DEFAULT NOW(),
   updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Table brands
CREATE TABLE ecoride.brands(
   id SERIAL PRIMARY KEY,
   name VARCHAR(50) NOT NULL,
   created_at TIMESTAMPTZ DEFAULT NOW(),
   updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Table cars
CREATE TABLE ecoride.cars(
   id SERIAL PRIMARY KEY,
   model VARCHAR(50) NOT NULL,
   registration VARCHAR(15) NOT NULL UNIQUE,
   first_registration_date DATE NOT NULL,
   energy energy NOT NULL,
   color VARCHAR(100),
   brand_id INT NOT NULL,
   user_id INT NOT NULL REFERENCES ecoride.users(id),  -- Propriétaire = conducteur
   created_at TIMESTAMPTZ DEFAULT NOW(),
   updated_at TIMESTAMPTZ DEFAULT NOW(),
   FOREIGN KEY(brand_id) REFERENCES ecoride.brands(id)
);

-- Table roles
CREATE TABLE ecoride.roles(
   id SERIAL PRIMARY KEY,
   name VARCHAR(50) NOT NULL UNIQUE,
   created_at TIMESTAMPTZ DEFAULT NOW(),
   updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Table carpoolings
CREATE TABLE ecoride.carpoolings(
   id SERIAL PRIMARY KEY,
   departure_date DATE NOT NULL,
   departure_time TIME NOT NULL,
   departure_location VARCHAR(200) NOT NULL,
   end_date DATE NOT NULL,
   end_time TIME NOT NULL,
   end_location VARCHAR(200) NOT NULL,
   status carpooling_status DEFAULT 'draft' NOT NULL,
   place_number SMALLINT NOT NULL,
   price DECIMAL(6, 2) NOT NULL CHECK (price > 2),  -- Prix > 2 crédits
   car_id INT NOT NULL,
   created_at TIMESTAMPTZ DEFAULT NOW(),
   updated_at TIMESTAMPTZ DEFAULT NOW(),
   FOREIGN KEY(car_id) REFERENCES ecoride.cars(id)
);

-- Table opinions (simplifiée)
CREATE TABLE ecoride.opinions(
   id SERIAL PRIMARY KEY,
   comment TEXT NOT NULL,
   note INT NOT NULL CHECK (note BETWEEN 1 AND 5),
   status opinion_status DEFAULT 'pending' NOT NULL,
   carpooling_id INT NOT NULL REFERENCES ecoride.carpoolings(id),  -- Lien au trajet
   author_id INT NOT NULL REFERENCES ecoride.users(id),  -- Auteur (passager)
   target_id INT NOT NULL REFERENCES ecoride.users(id), -- Cible de l'avis (chauffeur)
   validator_id INT REFERENCES ecoride.users(id),  -- Superviseur (NULL si non validé)
   validated_at TIMESTAMPTZ,  -- Date de validation (NULL si non validé)
   created_at TIMESTAMPTZ DEFAULT NOW(),
   updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Table transactions (pour suivre les crédits)
CREATE TABLE ecoride.transactions(
   id SERIAL PRIMARY KEY,
   amount DECIMAL(10, 2) NOT NULL CHECK (amount > 0),
   sender_id INT NOT NULL REFERENCES ecoride.users(id),  -- Expéditeur (passager)
   receiver_id INT NOT NULL REFERENCES ecoride.users(id),  -- Destinataire (conducteur ou société)
   carpooling_id INT REFERENCES ecoride.carpoolings(id),  -- Lien au trajet
   transaction_type VARCHAR(20) NOT NULL,  -- 'driver_fee', 'company_fee'
   created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Table carpoolings_users (participants aux trajets)
CREATE TABLE ecoride.carpoolings_users(
   carpooling_id INT NOT NULL,
   user_id INT NOT NULL,
   created_at TIMESTAMPTZ DEFAULT NOW(),
   PRIMARY KEY(carpooling_id, user_id),
   FOREIGN KEY(carpooling_id) REFERENCES ecoride.carpoolings(id),
   FOREIGN KEY(user_id) REFERENCES ecoride.users(id)
);

-- Table roles_users (rôles des utilisateurs)
CREATE TABLE ecoride.roles_users(
   role_id INT NOT NULL,
   user_id INT NOT NULL,
   created_at TIMESTAMPTZ DEFAULT NOW(),
   PRIMARY KEY(role_id, user_id),
   FOREIGN KEY(role_id) REFERENCES ecoride.roles(id),
   FOREIGN KEY(user_id) REFERENCES ecoride.users(id)
);