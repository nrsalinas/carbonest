
# coding: utf-8

# # Depuracion e integracion de datos mixtos
#
# El presente notebook realiza la exploración inicial y depuración de datos agregados de vegetación consolidados por el SMBYC.
#
# **Módulos requeridos:** Numpy y Pandas para la depuración de datos, SQLAlchemy para la inserción de información en las bases de datos.
#
# Las siguientes variables indican la ubicación de los archivos que contienen los datos sin depurar:
#
# 1. `asignacion`: Tabla en formato csv. Contiene información básica de las parcelas (ubicación, custodio, etc.).
#
# 2. `individuos`: Tabla en formato csv. Contiene medidas y demás datos relacionados con los individuos (diámetro, altura, parcela, placa, etc.).
#
# También es necesario indicar las credenciales de accesos al servidor MySQL a través de las variables `user` (nombre de usuario) y `password` (clave de acceso).
#
#

# In[ ]:


import pandas as pd
import numpy as np

# MySQL user and password
password = u""
user = u""

# Asignar nombres de archivos a variables
asignacion = "../data/quimera/asignacion.csv"
individuos =  "../data/quimera/newind.csv"


# In[ ]:


asig = pd.read_csv(asignacion, encoding = 'utf8')

# low_memory asume que los datos estan homogeneamente tipificados.
ind = pd.read_csv(individuos, low_memory=False, encoding = 'utf8')


# ### Variables para los nombres de las columnas
#
# A continuación se adjudica una variable a cada nombre de la columna en ambos archivos. Si los nombres no son los mencionados deben ser actualizados en concordancia. El nombre de la columna que contiene el indice de la parcela debe ser igual en ambos archivos.

# In[ ]:


# Variables de campos de tabla `individuos`

FID = u'FID' # Indice de medicion (int)
Plot = u'Plot' # Indice parcela (int)
D = u'D'# Diametro del tallo en cm (float)
H = u'H' # Altura total del tallo en m (float)
X = u'X' # Coordenada X en m (float)
Y = u'Y' # Coordenada Y en m (float)
Placa = u'Placa' # Placa de referencia del individuo (str, aunque la mayoria son int)
Densidad = u'Densidad' # Densidad de la madera en gr/ml (float)
Fuente_densidad = u'Fuente_densidad' # Referencia bibliografica de la densidad de la madera (str)
Habito = u'Habito' # Clasificacion de referencia (str: 'Arborea', 'Palma', 'No-Arborea', 'Exotica', 'Paramo', 'Mangle').
Entra_calculos = u'Entra_calculos' # Inclusion en analisis (str: 'Si', 'No')
Familia = u'Familia' # Familia taxonomica (str)
Autor_familia = u'Autor_familia' # Autor familia taxonomica (str)
Genero = u'Genero' # Genero taxonomica (str)
Autor_genero = u'Autor_genero' # Autor genero taxonomica (str)
Estado_epiteto = u'Estado_epiteto' # Incertidumbre de la determinacion especifica (str: 'aff.', 'cf.', 'vs.', 'gr.')
Epiteto = u'Epiteto' # Epiteto especifico, si indeterminado a especie contiene 'sp.' (str)
Autor_especie = u'Autor_especie' # Autor epiteto taxonomico (str)
Morfoespecie = u'Morfoespecie' # Concatenacion de los campos Genero y Epiteto (str).

fields_ind = [FID, Plot, D, H, X, Y, Placa, Densidad, Fuente_densidad, Habito, Entra_calculos, Familia, Autor_familia, Genero, Autor_genero, Estado_epiteto, Epiteto, Autor_especie, Morfoespecie]


# In[ ]:


# Variables de campos de tabla `asignacion`

Area = u'Area' # Superficie de la parcela en hectareas (float64)
Year = u'Year' # Año de levantamiento de datos (int64)
Tipo_parcela = u'Tipo_parcela' # Clase de parcela (str: 'Temporal', 'Permanente')
Custodio = u'Custodio' # Autor o custodio de la informacion (str)
Custodio_abreviado = u'Custodio_abreviado' # Abreviatura del autor o custodio de la informacion (str)
Parcela_original = u'Parcela_original' # Codigo de la parcela empleado por el custodio (str)
Proyecto = u'Proyecto' # Codigo del proyecto bajo el cual la parcela fue establecida (str)
PID = u'PID' # Que carajos es esto???????????????
X = u'X' # Coordenada X WGS84 zona 18N en m, origen en 0°, -75° (float64). Reformatear a numerico, aunque hay unos valores con dobles comas.
Y = u'Y' # Coordenada x WGS84 zona 18N en m, origen en 0°, -75° (float64). Reformatear a numerico, aunque hay unos valores con dobles comas.
X_MAGNA = u'X_MAGNA' # Coordenada x Magna en m (float64). Reformatear a numerico, aunque hay unos valores con dobles comas.
Y_MAGNA = u'Y_MAGNA' # Coordenada y Magna en m (float64). Reformatear a numerico, aunque hay unos valores con dobles comas.
Acceso = u'Acceso' # Clase de acceso permitido al IDEAM por el custodio (str: 'Confidencial','Público').
Departamento = u'Departamento' # Departamento str.
Municipio = u'Municipio' # Municipio str.
CAR = u'CAR' # Corporacion autonoma regional con jurisdiccion en el sitio de muestreo (str).
UAESPNN = u'UAESPNN' # Unidad del sistema de areas protegidas con jurisdiccion en el sitio de muestreo (str).
Region = u'Region' # Region geografica de Colombia (str: 'Amazonia', 'Caribe', 'Andes', 'Pacifico', 'Orinoquia', 'Andina').
Escenario_referencia = u'Escenario_referencia' # Unidad geografica de referencia (str: 'Amazonia', 'Noroccidental', 'Caribe', 'Suroccidental', 'Antioquia','Andes oriental', 'Eje cafetero', 'Nororiental', 'Orinoquia')
ECP = u'ECP' # ????????????????????????????????? (float64)
Holdridge = u'Holdridge' # Clasificacion climatica de Holdridge, modelo 2014 (str)
Provincia = u'Provincia' # Provincia bioclimatica, modelo 2014 (str: 'Wet forest', 'Moist forest', 'Dry forest')
Caldas_Lang = u'Caldas_Lang' # Clasificacion climatica Caldas-Lang, modelo 2014 (str)
Martonne = u'Martonne' # Clasificacion climatica Martonne, modelo 2014 (str: 'Bosque lluvioso','Bosque lluvioso estacional','Bosque húmedo','Bosque subhúmedo')
Eq1 = u'Eq1' # Valor de biomasa al aplicar la ecuacion 1 (int64)??????
Eq2 = u'Eq2' # Valor de biomasa al aplicar la ecuacion 2 (int64)??????
Eq3 = u'Eq3' # Valor de biomasa al aplicar la ecuacion 3 (int64)??????

fields_asig = [Plot, Area, Year, Tipo_parcela, Custodio, Custodio_abreviado, Parcela_original, Proyecto, PID, X, Y, X_MAGNA, Y_MAGNA, Acceso, Departamento, Municipio, CAR, UAESPNN, Region, Escenario_referencia, ECP, Holdridge, Provincia, Caldas_Lang, Martonne, Eq1, Eq2, Eq3]


# ### Verificación de tipos
# A continuación se verifica si los datos de ambas tablas están presentados en los tipos de datos esperados.

# In[ ]:


# Verificar si todas las columnas tienen el tipo de dato adecuado

for fi in [FID, Plot]:
    if ind[fi].dtype != np.int64:
        print "Campo {0} tiene tipo inapropiado ({1} en vez de int64).".format(fi, ind[fi].dtype)

for fi in [D, H, X, Y, Densidad]:
    if ind[fi].dtype != np.float64:
        print "Campo {0} tiene tipo inapropiado ({1}en vez de float64).".format(fi, ind[fi].dtype)

for fi in [Placa, Fuente_densidad, Habito, Familia, Autor_familia, Genero, Autor_genero, Estado_epiteto, Epiteto, Autor_especie, Morfoespecie]:
    non_strings = ind[fi].dropna()[~ind[fi].dropna().apply(type).eq(unicode)]
    if len(non_strings):
        print "Campo {0} tiene tipo inapropiado ({1} en vez de unicode).".format(fi, non_strings.dtype)

try:
    ind[Entra_calculos].replace(to_replace = [u'Si',u'No'], value = [True, False], inplace = True)
except TypeError, ErrorMessage:
    if ErrorMessage.args[0] == "Cannot compare types 'ndarray(dtype=bool)' and 'unicode'":
        pass
    else:
        raise
except:
    raise

if ind[Entra_calculos].dtype != np.bool_:
    print "Campo {0} tiene tipo inapropiado ({1} en vez de bool).".format(Entra_calculos, ind[Entra_calculos].dtype)


# Verificacion de tipo de datos en tabla asignacion

# Campo `Acceso` es insertado en la columna `AccesoPublico` de la base de datos, que es boolean.
# Sin embargo, para poder importarlo via mysqlimport es guardado en pandas como np.int64

asig[Acceso].replace(to_replace = [u'Confidencial',u'Público'], value = [0, 1], inplace = True)
asig[X].replace(to_replace=r',',value='',regex=True, inplace=True)
asig[Y].replace(to_replace=r',',value='',regex=True, inplace=True)
asig[X_MAGNA].replace(to_replace=r',',value='',regex=True, inplace=True)
asig[Y_MAGNA].replace(to_replace=r',',value='',regex=True, inplace=True)
asig[[X,Y,X_MAGNA,Y_MAGNA]] = asig[[X,Y,X_MAGNA,Y_MAGNA]].apply(pd.to_numeric)

for fi in [Plot, Year, X, Y, X_MAGNA, Y_MAGNA, Eq1, Eq2, Eq3, Acceso]:
    if asig[fi].dtype != np.int64:
        print "Campo {0} tiene tipo inapropiado ({1} en vez de int64).".format(fi, asig[fi].dtype)

for fi in [Area]:
    if asig[fi].dtype != np.float64:
        print "Campo {0} tiene tipo inapropiado ({1} en vez de float64).".format(fi, asig[fi].dtype)

for fi in [Tipo_parcela, Custodio, Custodio_abreviado, Parcela_original, Departamento, Municipio, CAR, UAESPNN, Region, Escenario_referencia, Holdridge, Provincia, Caldas_Lang, Martonne]:
    non_strings = asig[fi].dropna()[~asig[fi].dropna().apply(type).eq(unicode)]
    if len(non_strings):
        print "Campo {0} tiene tipo inapropiado ({1} en vez de unicode).".format(fi, non_strings.dtype)




# ### Verificación de rango de valores
#
# A continuación se verifica si los valores de cada columna corresponden a los rangos esperados. En este punto del proceso sólo se verifica que los valores tengan sentido lógico. Una mayor depuración de los datos se realizará después de que éstos sean incluidos en la base de datos.

# In[ ]:


#########################################
# Tabla individuos
#########################################

# Indice no debe contener duplicado
if len(ind[ind[FID].duplicated()]):
    print "Tabla {0} contiene indices duplicados.".format(individuos)

# Rango de diametro = 10-770 (diametro de General Sherman)
if ind[D].min() < 10:
    print "Existen valores de diametro inferiores a 10 cm"
if ind[D].max() > 770:
    print "Existen valores de diametro dudosamente altos"

# Rango de alturas = 1 - 100
if ind[H].min() < 1:
    print "Existen valores de altura inferiores a 1 m"
if ind[H].max() > 100:
    print "Existen valores de altura dudosamente altos"

# Rango de densidades de madera = 0.08 - 1.39 (Global Wood Density Database compilada por Chave
# y diponible en http://datadryad.org/repo/handle/10255/dryad.235)
if ind[Densidad].min() < 0.08:
    print "Existen valores de densidad inferiores a 0.8 gr/ml"
if ind[Densidad].max() > 1.39:
    print "Existen valores de densidad superiores a 1.39 gr/ml"

# Estados de incertidumbre taxonomica = 'aff.', 'cf.', 'vel sp. aff.'
########################################################
# Reemplazo de valores no aceptados detectados:
# 'vs.' reemplazado con 'vel sp. aff.'
# 'gr.' reemplazado con 'vel sp. aff.'
########################################################
ind[Estado_epiteto].replace(to_replace = [u'vs.', u'gr.'], value = [u'vel sp. aff.',u'vel sp. aff.'], inplace = True)

for est in ind[Estado_epiteto].dropna().unique():
    if est not in [u'aff.', u'cf.', u'vel sp. aff.']:
        print "{0} no es un estado de incertidumbre de determinacion aceptado".format(est)
        print ind[[Genero, Estado_epiteto, Epiteto]][ind[Estado_epiteto] == est]

# Informacion de la columna `Habito` debe ser distribuido en tres columnas: `Habito`,
# `Origen` y `Ecosistema`. Columnas `Origen` y `Ecosistema` deben ser creadas para tal
# proposito

ind.insert(10, u'Origen', value=u'Nativa')
ind.insert(12, u'Ecosistema', value=np.nan)
ind.loc[ind[Habito] == u'No-Arborea', Habito] = u'No arborea'
ind.loc[ind[Habito] == u'Exotica', u'Origen'] = u'Introducida'
ind.loc[ind[Habito] == u'Paramo' , u'Ecosistema'] = u'Paramo'
ind.loc[ind[Habito] == u'Mangle' , u'Ecosistema'] = u'Manglar'
ind[Habito].replace(to_replace = [u'Exotica',u'Paramo',u'Mangle'], value = np.nan, inplace = True)

# Verificar que `Habito`, `Origen` y `Ecosistema` contienen valores validos
for hab in ind[Habito].dropna().unique():
    if hab not in [u'Arborea', u'Palma', u'Liana', u'No arborea']:
        print "{0} no es un valor aceptado de `Habito`".format(hab)
        print ind[[Genero, Epiteto, Habito]][ind[Habito] == hab]

for ori in ind[u'Origen'].dropna().unique():
    if ori not in [u'Nativa', u'Introducida']:
        print "{0} no es un valor aceptado de `Origen`".format(ori)
        print ind[[Genero, Epiteto, u'Origen']][ind[u'Origen'] == ori]

for eco in ind[u'Ecosistema'].dropna().unique():
    if eco not in [u'Paramo', u'Manglar']:
        print "{0} no es un valor aceptado de `Ecosistema`".format(eco)
        print ind[[Genero, Epiteto, u'Ecosistema']][ind[u'Ecosistema'] == eco]


#########################################
# Tabla asignacion
#########################################

# Indice de parcela no debe tener duplicados
if len(asig[asig[Plot].duplicated()]):
    print "Tabla {0} contiene indices duplicados.".format(asignacion)

# Verificar areas, rango permitido: 0.02-25 ha
if asig[Area].min() < 0.02:
    print "Algunos valores de area de parcela estan por debajo del valor minimo"
if asig[Area].max() > 25:
    print "Algunos valores de area de parcela son sospechosamente altos"

# Rango de años permitido: 1990-2017
if asig[Year].min() < 1990:
    print "Realmente hay datos levantados antes de 1990?"
if asig[Year].max() > 2017:
    print "Parece que algunos datos provienen del futuro. Verificar fechas."

# Verificar correspondencia 1:1 entre el indice propio de parcela y el indice del custodio
if filter(lambda x: x != 1, asig.groupby([Plot, Parcela_original]).size()):
    print "No hay concordancia entre las asignaciones de indices propios y externos:"
    multiPlots = asig.groupby([Plot, Parcela_original]).size().reset_index()
    print multiPlots[multiPlots[0] > 1]

# Verificar tipo de parcela valido: 'temporal', 'permanente'
for par in asig[Tipo_parcela].dropna().unique():
    if par not in [u'Permanente',u'Temporal']:
        print "{0} no es un tipo de parcela aceptado".format(par)

# Varificar rango de coordenadas.
x_rango = (-231000, 1410000)
y_rango = (-480000, 1500000)
if asig[X].min() < x_rango[0] or asig[X].max() > x_rango[1]:
    print "Coordenadas X fuera del rango permitido"
if asig[Y].min() < y_rango[0] or asig[Y].max() > y_rango[1]:
    print "Coordenadas Y fuera del rango permitido"

# Verificar rango Magna
xm_rango = (167000, 1810000)
ym_rango = (23000, 1900000)
if asig[X_MAGNA].min() < xm_rango[0] or asig[X_MAGNA].max() > xm_rango[1]:
    print "Coordenadas X Magna fuera del rango permitido"
if asig[Y_MAGNA].min() < ym_rango[0] or asig[Y_MAGNA].max() > ym_rango[1]:
    print "Coordenadas Y Magna fuera del rango permitido"

for acc in asig[Acceso].unique():
    if acc not in [0, 1]:
        print "Clase de acceso a datos de parcela tiene valores no aceptados"


# # Inclusion de información en la base de datos
# Se incluyen los datos depurados en la base de datos MySQL a través del módulo SQLAlchemy. El esquema de la base de datos debe ser incluido con anterioridad al servidor local. Una copia del esquema está disponible en el archivo `Esquema_Quimera.sql`.

# In[ ]:


import sqlalchemy as al
engine = al.create_engine(
    'mysql+mysqldb://{0}:{1}@localhost/Quimera?charset=utf8&use_unicode=1'.format(user, password),
    encoding='utf-8')

con = engine.connect()


# In[ ]:


# Crear una lista unica de especies y escribirla a la tabla Taxonomia

tax = {}

for row in ind[[Familia, Genero, Epiteto, Autor_genero, Autor_especie, Habito, 'Origen']].itertuples():
    tax[(row[1], row[2], row[3])] = (row[4], row[5], row[6], row[7])

taxtemp = {Familia:[], Genero:[], Epiteto:[], Autor_genero:[], Autor_especie:[], Habito:[], 'Origen':[]}

for (fam, gen, epi) in tax:
    taxtemp[Familia].append(fam)
    taxtemp[Genero].append(gen)
    taxtemp[Epiteto].append(epi)
    taxtemp[Autor_genero].append(tax[(fam, gen, epi)][0])
    taxtemp[Autor_especie].append(tax[(fam, gen, epi)][1])
    taxtemp[Habito].append(tax[(fam, gen, epi)][2])
    taxtemp['Origen'].append(tax[(fam, gen, epi)][3])

tax = None
taxdf = pd.DataFrame.from_dict(taxtemp)
taxtemp = None

if taxdf.index[0] == 0:
    taxdf.index += 1

taxdf[u'Fuente'] = 1

taxdf.rename(columns={Familia:u'Familia', Genero:u'Genero', Autor_genero:u'AutorGenero', Epiteto:u'Epiteto',
    Autor_especie:u'AutorEpiteto', Habito:u'Habito'}).to_sql('Taxonomia', con,
    if_exists='append', index_label=u'TaxonID')


# In[ ]:


# Insertando la informacion de determinaciones

if u'Taxon' not in taxdf.columns:
    taxdf[u'Taxon'] = taxdf.index

if 'Taxon' not in ind:
    ind = ind.merge(taxdf[[Familia, Genero, Epiteto, u'Taxon']], on=[u'Familia',u'Genero',u'Epiteto'],
            how='left', suffixes = ['_l', '_r']).rename(columns={Estado_epiteto:u'Incert'})

if ind.index[0] == 0:
    ind.index += 1

ind[['Taxon', 'Incert']].to_sql('Determinaciones', con, if_exists='append', index_label='DetID')


# In[ ]:


# Guardando los datos en la tabla Individuos

ind[[FID, D, H, Placa, Plot , X, Y]].merge(asig[[Plot,Year]], on=Plot, how='left').rename(
    columns={FID:'IndividuoID', D:'Diametro', H:'Altura', Year:'Year', Placa:'Placa', Plot:'Plot',
    X:'X', Y:'Y'}).to_sql('Individuos', con, if_exists='append', index_label='Dets')


# In[ ]:


# Tabla Parcelas

asig[[Plot, Area, Custodio, Custodio_abreviado, Proyecto, X, Y, X_MAGNA, Y_MAGNA, Departamento,
    Municipio, CAR, UAESPNN, Region, Escenario_referencia, Acceso]].rename(columns=
    {Plot:'PlotID', Area:'Area', Custodio:'Custodio', Custodio_abreviado:'CustodioAbreviado',
    Proyecto:'Proyecto', X:'X', Y:'Y', X_MAGNA:'XMAGNA', Y_MAGNA:'YMAGNA', Departamento:'Departamento',
    Municipio:'Municipio', CAR:'CAR', UAESPNN:'UAESPNN', Region:'Region', Escenario_referencia:
    'EscenarioReferencia', Acceso:'AccesoPublico'}).to_sql('Parcelas', con,
    if_exists='append', index=False)


# In[ ]:


# Tabla Fuentes

fuen = ind.groupby(by=Fuente_densidad).size().reset_index().drop(labels=0, axis=1)

if fuen.index[0] == 0:
    fuen.index += 2
# Numeración del indice comienza en 2 porque ya existe una entrada
# en la tabla: `Custodio`

fuen.rename(columns={Fuente_densidad:'Nombre'}).to_sql('Fuentes', engine, if_exists='append',
    index_label = 'FuenteID')


# In[ ]:


# Tabla Densidades

if 'Fuente' not in fuen.columns:
    fuen['Fuente'] = fuen.index

if 'Fuente' not in ind.columns:
    ind = ind.merge(fuen, how='left', on=Fuente_densidad)
    ind.index += 1

dens = ind.groupby(by=['Taxon', Densidad, 'Fuente']).size().reset_index().drop(axis=1, labels=0)

if dens.index[0] == 0:
    dens.index += 1

dens.to_sql('Densidades', con, if_exists='append', index_label = 'DensidadID')


# In[ ]:


con.close()
