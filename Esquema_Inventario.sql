/*###########################################################
Version 2:

- Fuentes en Taxonomia son referencias a FuenteID en Fuentes

- Primera fila en Fuentes es 'Socio', la fuente de toda la
  informacion taxonomica inicial.

###########################################################*/

DROP DATABASE IF EXISTS IFN;
CREATE DATABASE IFN CHARACTER SET utf8 COLLATE utf8_bin;

USE IFN;

DROP TABLE IF EXISTS Detritos;
CREATE TABLE Detritos (
	DetritoID INT NOT NULL UNIQUE,
	Plot INT NOT NULL, # referencia a Conglomerados.PlotID
	Transecto ENUM('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H') DEFAULT NULL,
	Seccion TINYINT DEFAULT NULL, # 1, 2, 3
	Pieza INT DEFAULT NULL,
	Tipo ENUM('DFM', 'DGM') DEFAULT NULL,
	Distancia FLOAT DEFAULT NULL,
	Azimut FLOAT DEFAULT NULL, # grados 0-360
	Diametro1 FLOAT DEFAULT NULL, # cm
	Diametro2 FLOAT DEFAULT NULL, # cm
	Inclinacion FLOAT DEFAULT NULL,
	PetrProf FLOAT DEFAULT NULL, # Profundidad en cm alcanzada por el penetrometro
	PetrGolpes INT DEFAULT NULL, # Golpes ejercidos con el penetrometro
	PesoRodaja FLOAT DEFAULT NULL, # Peso en gr
	PesoMuestra FLOAT DEFAULT NULL, # Peso en gr
	PesoSeco FLOAT DEFAULT NULL, # Peso en gr
	Espesor1 FLOAT DEFAULT NULL, # longitud en cm
	Espesor2 FLOAT DEFAULT NULL, # longitud en cm
	Espesor3 FLOAT DEFAULT NULL, # longitud en cm
	Espesor4 FLOAT DEFAULT NULL, # longitud en cm
	Volumen FLOAT DEFAULT NULL, # ml
	Densidad FLOAT DEFAULT NULL, # gr / ml
	Fecha_mod TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
	PRIMARY KEY (DetritoID)
	)
	ENGINE = INNODB DEFAULT CHARSET=UTF8;


DROP TABLE IF EXISTS Tallos;
CREATE TABLE Tallos (
	#
	# DEBE SER AUTO_INCREMENT?
	#
	TalloID INT NOT NULL UNIQUE,
	Diametro1 FLOAT DEFAULT NULL,
	Diametro2 FLOAT DEFAULT NULL,
	DiametroP FLOAT DEFAULT NULL,
	EquipoDiam ENUM('CD', 'FO', 'CA', 'CM') DEFAULT NULL,
	Tamano ENUM('B', 'L', 'F', 'FG'), # Brinzales, Latizales, Fustales, Fustales Grandes
	FormaFuste ENUM('CIL', 'RT','IRR','FA','HI','Q') DEFAULT NULL,
	AlturaFuste FLOAT DEFAULT NULL,
	AlturaTotal FLOAT DEFAULT NULL,
	EquipoAlt ENUM('HI', 'VT', 'CL', 'CM', 'VX', 'FL', 'CD') DEFAULT NULL,
	Individuo INT NOT NULL, # referencia a Individuos.IndividuoID

	# Campos especificos para Arboles Muerts en Pie
	Condicion ENUM('MP', 'TO', 'VP', 'MC', 'M') DEFAULT NULL,
	POM FLOAT DEFAULT NULL,
	DANO ENUM('Q', 'DB', 'SD', 'DM', 'IRR', 'EB') DEFAULT NULL, # solo AMP
	PetrProf FLOAT DEFAULT NULL, # Profundidad en cm alcanzada por el penetrometro, solo AMP
	PetrGolpes INT DEFAULT NULL, # Golpes ejercidos con el penetrometro, solo AMP

	Fecha_mod TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, # Fecha de insercion o modificación del registro en la db
	PRIMARY KEY (TalloID)
	)
	ENGINE = INNODB DEFAULT CHARSET=UTF8;


DROP TABLE IF EXISTS Individuos;
CREATE TABLE Individuos (
	#
	# Confirmar si el indice deberia ser AUTO_INCREMENT
	#
	IndividuoID INT AUTO_INCREMENT NOT NULL,
	Plot INT DEFAULT NULL, # referencia a Conglomerados.PlotID
	Subparcela TINYINT DEFAULT NULL,
	Azimut FLOAT DEFAULT NULL,
	Distancia FLOAT DEFAULT NULL,
	Dets INT DEFAULT NULL, # Historia de determinaciones, referencia a Determinaciones.DetID. Deben ser valores unicos por individuos vivos, NULL si es individuo muerto.
	Fecha_mod TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
	PRIMARY KEY (IndividuoID)
	)
	ENGINE = INNODB DEFAULT CHARSET=UTF8;


DROP TABLE IF EXISTS Taxonomia;
CREATE TABLE Taxonomia (
	#
	# Una especie puede tener varios valores de Habito???
	#
	TaxonID INT AUTO_INCREMENT NOT NULL,
	Fuente INT DEFAULT NULL, /* Origen nombre. Referencia a Fuentes.FuenteID */
	Familia VARCHAR(255) DEFAULT NULL,
	Genero VARCHAR(255) DEFAULT NULL,
	Epiteto VARCHAR(255) DEFAULT NULL,
	Autor VARCHAR(255) DEFAULT NULL,
	SinonimoDe INT DEFAULT NULL, /* Referencia a Taxonomia.TaxonID. Si es aceptado entonces NULL */
	Fecha_mod TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, /* Fecha de insercion del registro en la db */
	PRIMARY KEY (TaxonID)
	)
	ENGINE = INNODB DEFAULT CHARSET=UTF8;


DROP TABLE IF EXISTS Determinaciones;
CREATE TABLE Determinaciones (
	DetID INT AUTO_INCREMENT NOT NULL,
	Taxon INT NOT NULL, # Referencia a Taxonomia.TaxonID
	Incert ENUM('aff.', 'cf.', 'vel sp aff.'),
	DetPrevia INT DEFAULT NULL, # Referencia a otro DetID, si es la primera entonces NULL
	Fecha_mod TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, # Fecha de insercion del registro en la db
	PRIMARY KEY (DetID)
	)
	ENGINE = INNODB DEFAULT CHARSET=UTF8;


DROP TABLE IF EXISTS Conglomerados;
CREATE TABLE Conglomerados (
	PlotID INT NOT NULL UNIQUE,
	Departamento VARCHAR(50),
	Region ENUM('Amazonia', 'Andes', 'Pacifico', 'Orinoquia', 'Caribe') NOT NULL,
	Fecha YEAR, # Año toma de  datos
	Socio VARCHAR(255),
	SFPC TINYINT NOT NULL, # Subparcelas donde se tomó la medición de Carbono ?????
	Fecha_mod TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
	PRIMARY KEY (PlotID)
	)
	ENGINE = INNODB DEFAULT CHARSET=UTF8;

DROP TABLE IF EXISTS Coordenadas;
CREATE TABLE Coordenadas (
	Plot INT, # Referencia a Conglomerados.PlotID
	SPF TINYINT DEFAULT NULL,
	Latitud FLOAT DEFAULT NULL,
	Longitud FLOAT DEFAULT NULL,
	ZV FLOAT DEFAULT NULL,
	ZonaVida VARCHAR(60) DEFAULT NULL,
	Eq TINYINT DEFAULT NULL,
	ChaveE FLOAT DEFAULT NULL,
	PRIMARY KEY (Plot, SPF)
	)
	ENGINE = INNODB DEFAULT CHARSET=UTF8;

/*##########################################################
# Las densidades son valores asignados a una categoria
# taxonomica (especie, genero, familia, etc.). Un taxon
# puede tener varios valores de densidad.
#########################################################*/
DROP TABLE IF EXISTS Densidades;
CREATE TABLE Densidades (
	DensidadID INT AUTO_INCREMENT NOT NULL,
	Densidad FLOAT NOT NULL,
	Taxon INT NOT NULL,  # Referencia a Taxonomia.TaxonID
	Fuente INT NOT NULL, # Referencia a Fuentes.FuenteID
	PRIMARY KEY (DensidadID)
	)
	ENGINE = INNODB DEFAULT CHARSET=UTF8;

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
	ENGINE = INNODB DEFAULT CHARSET=UTF8;

INSERT INTO Fuentes (FuenteID, Nombre, Acronimo, Year)
	VALUES (1, 'Socio', 'Socio', 2017);



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

ALTER TABLE Taxonomia
ADD FOREIGN KEY tax2fuent (Fuente)
REFERENCES Fuentes (FuenteID)
ON DELETE RESTRICT
ON UPDATE CASCADE;
