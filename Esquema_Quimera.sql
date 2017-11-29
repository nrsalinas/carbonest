#
# Delete database of exists
#

DROP DATABASE IF EXISTS Quimera;
CREATE DATABASE Quimera;

USE Quimera;

DROP TABLE IF EXISTS Mediciones;
CREATE TABLE Mediciones (
	#
	# Confirmar si el indice deberia ser AUTOINCREMENT
	#
	MedicionID INT NOT NULL,
	Diametro FLOAT NOT NULL,
	Altura FLOAT,
	Individuo INT NOT NULL, # referencia a Individuos.IndividuoID
	Year YEAR,
	Fecha_mod TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, # Fecha de insercion o modificación del registro en la db
	PRIMARY KEY (MedicionID)
	)
	ENGINE = INNODB;

DROP TABLE IF EXISTS Individuos;
CREATE TABLE Individuos (
	#
	# Confirmar si el indice deberia ser AUTOINCREMENT
	#
	IndividuoID INT NOT NULL,
	Dets INT NOT NULL UNIQUE, # Historia de determinaciones, referencia a Determinaciones.DetID. Deben ser valores unicos por individuo.
	Placa VARCHAR(255) DEFAULT NULL,
	Plot INT NOT NULL, # referencia a Parcelas.PlotID
	X FLOAT DEFAULT NULL,
	Y FLOAT DEFAULT NULL,
	PRIMARY KEY (IndividuoID)
	)
	ENGINE = INNODB;

DROP TABLE IF EXISTS Parcelas;
CREATE TABLE Parcelas (
	PlotID INT NOT NULL,
	Area FLOAT,
	Custodio VARCHAR(255) NOT NULL,
	CustodioAbbreviado VARCHAR(255) NOT NULL,
	Proyecto VARCHAR(255) DEFAULT NULL,
	X FLOAT NOT NULL,
	Y FLOAT NOT NULL,
	XMAGNA FLOAT NOT NULL,
	YMAGNA FLOAT NOT NULL,
	Departamento VARCHAR(255) NOT NULL,
	Municipio VARCHAR(255) DEFAULT NULL,
	CAR VARCHAR(255) DEFAULT NULL,
	UAESPNN VARCHAR(255) DEFAULT NULL,
	Region VARCHAR(255) DEFAULT NULL,
	EscenarioReferencia VARCHAR(255) DEFAULT NULL,
	Ecosistema VARCHAR(255) DEFAULT NULL, # Manglar, Paramo, etc
	Acceso_publico BOOL NOT NULL DEFAULT FALSE,
	PRIMARY KEY (PlotID)
	)
	ENGINE = INNODB;

DROP TABLE IF EXISTS Taxonomia;
CREATE TABLE Taxonomia (
	#
	# Una especie puede tener varios valores de Habito???
	#
	TaxonID INT AUTO_INCREMENT NOT NULL,
	Fuente VARCHAR(255) NOT NULL DEFAULT 'Custodio', # Origen nombre.
	Familia VARCHAR(255),
	Genero VARCHAR(255),
	AutorGenero VARCHAR(255),
	Epiteto VARCHAR(255),
	AutorEpiteto VARCHAR(255),
	SinonimoDe INT DEFAULT NULL, # Referencia a Taxonomia.TaxonID. Si es aceptado entonces NULL
	Habito ENUM('Arborea', 'Palma', 'Liana', 'No arborea'),
	Origen ENUM('Nativa', 'Introducida'),
	Fecha_mod TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, # Fecha de insercion del registro en la db
	PRIMARY KEY (TaxonID)
	)
	ENGINE = INNODB;

DROP TABLE IF EXISTS Determinaciones;
CREATE TABLE Determinaciones (
	DetID INT AUTO_INCREMENT NOT NULL,
	Taxon INT NOT NULL, # Referencia a Taxonomia.TaxonID
	Incert ENUM('aff.', 'cf.', 'vel sp aff.'),
	DetPrevia INT DEFAULT NULL, # Referencia a otro DetID, si es la primera entonces NULL
	Fecha_mod TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, # Fecha de insercion del registro en la db
	PRIMARY KEY (DetID)
	)
	ENGINE = INNODB;

DROP TABLE IF EXISTS Densidades;
CREATE TABLE Densidades (
	DensidadID INT AUTO_INCREMENT NOT NULL,
	Densidad FLOAT NOT NULL,
	Taxon INT NOT NULL,  # Referencia a Taxonomia.TaxonID
	Fuente INT NOT NULL, # Referencia a Fuentes.FuenteID
	PRIMARY KEY (DensidadID)
	)
	ENGINE = INNODB;

DROP TABLE IF EXISTS Fuentes;
CREATE TABLE Fuentes (
	FuenteID INT AUTO_INCREMENT NOT NULL,
	Nombre VARCHAR(255) NOT NULL,
	Acronimo VARCHAR(10) DEFAULT NULL,
	Url VARCHAR(255) DEFAULT NULL,
	Year INT DEFAULT NULL,
	Citacion TEXT DEFAULT NULL,
	PRIMARY KEY (FuenteID)
	)
	ENGINE = INNODB;


# Foreign keys

ALTER TABLE Mediciones
ADD FOREIGN KEY med2ind (Individuo)
REFERENCES Individuos (IndividuoID)
ON DELETE RESTRICT
ON UPDATE CASCADE;

ALTER TABLE Individuos
ADD FOREIGN KEY ind2det (Dets)
REFERENCES Determinaciones (DetID)
ON DELETE RESTRICT
ON UPDATE CASCADE;

ALTER TABLE Individuos
ADD FOREIGN KEY ind2parc (Plot)
REFERENCES Parcelas (PlotID)
ON DELETE RESTRICT
ON UPDATE CASCADE;

ALTER TABLE Determinaciones
ADD FOREIGN KEY det2tax (Taxon)
REFERENCES Taxonomia (TaxonID)
ON DELETE RESTRICT
ON UPDATE CASCADE;

ALTER TABLE Densidades
ADD FOREIGN KEY den2tax (Taxon)
REFERENCES Taxonomia (TaxonID)
ON DELETE RESTRICT
ON UPDATE CASCADE;

ALTER TABLE Densidades
ADD FOREIGN KEY den2fuent (Fuente)
REFERENCES Fuentes (FuenteID)
ON DELETE RESTRICT
ON UPDATE CASCADE;
