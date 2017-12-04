import MySQLdb
import pandas as pd
import numpy as np


asignacion = "../data/quimera/asignacion.csv"
asig = pd.read_csv(asignacion)


Area = 'Area' # Superficie de la parcela en hectareas (float64)
Year = 'Year' # Año de levantamiento de datos (int64)
Tipo_parcela = 'Tipo_parcela' # Clase de parcela (str: 'Temporal', 'Permanente')
Custodio = 'Custodio' # Autor o custodio de la informacion (str)
Custodio_abreviado = 'Custodio_abreviado' # Abreviatura del autor o custodio de la informacion (str)
Parcela_original = 'Parcela_original' # Codigo de la parcela empleado por el custodio (str)
Proyecto = 'Proyecto' # Codigo del proyecto bajo el cual la parcela fue establecida (str)
PID = 'PID' # Que carajos es esto???????????????
X = 'X' # Coordenada X WGS84 zona 18N en m, origen en 0°, -75° (float64). Reformatear a numerico, aunque hay unos valores con dobles comas.
Y = 'Y' # Coordenada x WGS84 zona 18N en m, origen en 0°, -75° (float64). Reformatear a numerico, aunque hay unos valores con dobles comas.
X_MAGNA = 'X_MAGNA' # Coordenada x Magna en m (float64). Reformatear a numerico, aunque hay unos valores con dobles comas.
Y_MAGNA = 'Y_MAGNA' # Coordenada y Magna en m (float64). Reformatear a numerico, aunque hay unos valores con dobles comas.
Acceso = 'Acceso' # Clase de acceso permitido al IDEAM por el custodio (str: 'Confidencial','Público').
Departamento = 'Departamento' # Departamento str.
Municipio = 'Municipio' # Municipio str.
CAR = 'CAR' # Corporacion autonoma regional con jurisdiccion en el sitio de muestreo (str).
UAESPNN = 'UAESPNN' # Unidad del sistema de areas protegidas con jurisdiccion en el sitio de muestreo (str).
Region = 'Region' # Region geografica de Colombia (str: 'Amazonia', 'Caribe', 'Andes', 'Pacifico', 'Orinoquia', 'Andina').
Escenario_referencia = 'Escenario_referencia' # Unidad geografica de referencia (str: 'Amazonia', 'Noroccidental', 'Caribe', 'Suroccidental', 'Antioquia','Andes oriental', 'Eje cafetero', 'Nororiental', 'Orinoquia')
ECP = 'ECP' # ????????????????????????????????? (float64)
Holdridge = 'Holdridge' # Clasificacion climatica de Holdridge, modelo 2014 (str)
Provincia = 'Provincia' # Provincia bioclimatica, modelo 2014 (str: 'Wet forest', 'Moist forest', 'Dry forest')
Caldas_Lang = 'Caldas_Lang' # Clasificacion climatica Caldas-Lang, modelo 2014 (str)
Martonne = 'Martonne' # Clasificacion climatica Martonne, modelo 2014 (str: 'Bosque lluvioso','Bosque lluvioso estacional','Bosque húmedo','Bosque subhúmedo')
Eq1 = 'Eq1' # Valor de biomasa al aplicar la ecuacion 1 (int64)??????
Eq2 = 'Eq2' # Valor de biomasa al aplicar la ecuacion 2 (int64)??????
Eq3 = 'Eq3' # Valor de biomasa al aplicar la ecuacion 3 (int64)??????


def format2str(x):
    out = ""
    if x is np.nan or x is None:
        out = "NULL"
    elif isinstance(x, bool):
        if x == True:
            out = "TRUE"
        elif x == False:
            out = "FALSE"
    elif isinstance(x, str):
        out = "'{0}'".format(x)
    elif isinstance(x, int) or isinstance(x, float):
        out = "{0}".format(x)
    return out



db = MySQLdb.connect(host="localhost", user="root", passwd="", db="Quimera")

cursor = db.cursor()

cursor.execute("SET FOREIGN_KEY_CHECKS = 0")


for row in asig[[Plot, Area, Custodio, Custodio_abreviado, Proyecto, X, Y, X_MAGNA, Y_MAGNA, Departamento, Municipio, CAR, UAESPNN, Region, Escenario_referencia, Acceso]].itertuples():
    myrow = map(format2str, list(row))
    query = "INSERT INTO Parcelas (PlotID, Area, Custodio, CustodioAbbreviado, Proyecto, X, Y, XMAGNA, YMAGNA, Departamento, Municipio, CAR, UAESPNN, Region, EscenarioReferencia, Acceso_Publico) VALUES ({0[1]}, {0[2]}, {0[3]}, {0[4]}, {0[5]}, {0[6]}, {0[7]}, {0[8]}, {0[9]}, {0[10]}, {0[11]}, {0[12]}, {0[13]}, {0[14]}, {0[15]}, {0[16]})".format(myrow)
    
    cursor.execute(query)
    db.commit()

cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
db.close()
