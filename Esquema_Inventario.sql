DROP DATABASE IF EXISTS IFN;
CREATE DATABASE IFN;

USE IFN;

DROP TABLE IF EXISTS Detritos;
CREATE TABLE Detritos (
	DetritoID INT NOT NULL UNIQUE,
	Plot INT NOT NULL, # referencia a Conglomerados.PlotID
	Transecto ENUM('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H') NOT NULL,
	Seccion TINYINT NOT NULL, # 1, 2, 3
	Pieza INT NOT NULL,
	Tipo ENUM('DFM', 'DGM') NOT NULL,
	Distancia FLOAT NOT NULL,
	Azimut FLOAT NOT NULL, # grados 0-360
	Diametro1 FLOAT NOT NULL, # cm
	Diametro2 FLOAT, # cm
	Inclinacion FLOAT NOT NULL,
	PetrProf FLOAT DEFAULT NULL, # Profundidad en cm alcanzada por el penetrometro
	PetrGolpes INT DEFAULT NULL, # Golpes ejercidos con el penetrometro
	PesoRodaja FLOAT DEFAULT NULL, # Peso en gr
	PesoMuestra FLOAT DEFAULT NULL, # Peso en gr
	PesoSeco FLOAT NOT NULL, # Peso en gr
	Espesor1 FLOAT NOT NULL, # longitud en cm
	Espesor2 FLOAT, # longitud en cm
	Espesor3 FLOAT, # longitud en cm
	Espesor4 FLOAT, # longitud en cm
	Volumen FLOAT, # ml
	Densidad FLOAT, # gr / ml
	Fecha_mod TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
	PRIMARY KEY (DetritoID)
	)


DROP TABLE IF EXISTS Tallos;
CREATE TABLE Tallos (
	#
	# DEBE SER AUTO_INCREMENT?
	#
	TalloID INT NOT NULL UNIQUE,
	Diametro1 FLOAT NOT NULL,
	Diametro2 FLOAT,
	DiametroP FLOAT NOT NULL,
	Tamano ENUM('B', 'L', 'F', 'FG'), # L, F, FG
	AlturaFuste FLOAT,
	AlturaTotal FLOAT NOT NULL,
	Individuo INT NOT NULL, # referencia a Individuos.IndividuoID
	#
	# Incluir fecha de medicion?
	#
	# Fecha DATE # yyyy-mm-dd No especificada en la hoja de calculo original
	Fecha_mod TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, # Fecha de insercion o modificación del registro en la db
	PRIMARY KEY (TalloID)
	)
	ENGINE = INNODB;


DROP TABLE IF EXISTS Individuos;
CREATE TABLE Individuos (
	#
	# Confirmar si el indice deberia ser AUTOINCREMENT
	#
	IndividuoID INT NOT NULL,
	Plot INT NOT NULL, # referencia a Conglomerados.PlotID
	Azimut FLOAT NOT NULL,
	Distancia FLOAT NOT NULL,
	Dets INT NOT NULL UNIQUE, # Historia de determinaciones, referencia a Determinaciones.DetID. Deben ser valores unicos por individuo.
	Fecha_mod TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
	PRIMARY KEY (IndividuoID)
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


DROP TABLE IF EXISTS Conglomerados;
CREATE TABLE Conglomerados (
	PlotID INT NOT NULL UNIQUE,
	Departamento VARCHAR(50),
	Region ENUM('Amazonia', 'Andes', 'Pacifico', 'Orinoquia', 'Caribe') NOT NULL,
	Fecha YEAR, # Año toma de  datos
	Socio VARCHAR(255),
	SFP-C TINYINT NOT NULL, # No. de subparcelas establecidas ?????
	Fecha_mod TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
	PRIMARY KEY (PlotID)
	)
	ENGINE = INNODB;

# Foreign keys
ALTER TABLE Detritos
ADD FOREIGN KEY detr2plot (Plot)
REFERENCES Conglomerados (PlotID)
ON DELETE RESTRICT
ON UPDATE CASCADE;

ALTER TABLE Tallos
ADD FOREIGN KEY tallo2ind (Individuo)
REFERENCES Individuos (IndividuoID)
ON DELETE RESTRICT
ON UPDATE CASCADE;

ALTER TABLE Individuos
ADD FOREIGN KEY ind2plot (Plot)
REFERENCES Conglomerados (PlotID)
ON DELETE RESTRICT
ON UPDATE CASCADE;

ALTER TABLE Individuos
ADD FOREIGN KEY ind2dete (Dets)
REFERENCES Determinaciones (DetID)
ON DELETE RESTRICT
ON UPDATE CASCADE;

ALTER TABLE Determinaciones
ADD FOREIGN KEY dete2tax (Taxon)
REFERENCES Taxonomia (TaxonID)
ON DELETE RESTRICT
ON UPDATE CASCADE;
