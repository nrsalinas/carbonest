import pandas as pd
import sqlalchemy as al
import numpy as np
import wood_density as wd
import allometry

################################################################################
#
# Es necesario obtener promedios por parcela de densidades de individuos vivos
# para calcular la necromasa de los arboles muertos en pie
#
################################################################################


user = ''
password = ''
database = ''

engine = al.create_engine('mysql+mysqldb://{0}:{1}@localhost/{2}?charset=utf8&use_unicode=1&unix_socket=/var/run/mysqld/mysqld.sock'.format(user, password, database))

conn = engine.connect()

query = "SELECT Plot,TalloID,Diametro1,Diametro2,DiametroP,AlturaTotal,Tamano,PetrProf,PetrGolpes FROM Tallos LEFT JOIN Individuos ON IndividuoID=Individuo WHERE Dets IS NULL"

amp = pd.read_sql_query(query, conn, index_col="TalloID")
