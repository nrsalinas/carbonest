
# coding: utf-8

# # Depuracion datos Inventario Forestal Nacional
# 
# El presente notebook realiza la exploración inicial y depuración de datos del Inventario Forestal Nacional.
# 
# **Módulos requeridos:** Numpy y Pandas para la depuración de datos, SQLAlchemy para la inserción de información en las bases de datos.
# 
# Las siguientes variables indican la ubicación de las tablas de entrada en formato csv:
# 
# 1. `detritos`: Contiene los mediciones realizadas en detritos de madera.
# 
# 2. `ampie`: Mediciones de árboles muertos en pie.
#     
# 3. `vegetacion`: Mediciones de árboles vivos.
# 
# 4. `generalInfo`: Informacion general de cada conglomerado
# 
# 5. `coordenadas`: Coordenadas de parcelas
# 
# También es necesario indicar las credenciales de accesos al servidor MySQL a través de las variables `user` (nombre de usuario) y `password` (clave de acceso).  
# 
# 

# In[ ]:


import pandas as pd
import numpy as np
import codecs as cd

# Si se quieren realizar visualizaciones en las celdas:
# %matplotlib inline

# Si el script es ejecutado interactivamente (como un cuaderno Jupyter, por ejemplo)
# la variable `interactive` debe ser `True`, de lo contrario los reportes de error
# serán guardados en un archivo de texto (`logfile`).
interactive = False

# Archivo con reportes de error
logfile = u"revisar.txt"

logbuffer = u""

# MySQL user and password
password = u""
user = u""

# Asignar nombres de archivos a variables
detritos = u"../data/IFN/detritos.csv"
ampie =  u"../data/IFN/dasometricos/amp.csv"
vegetacion = u"../data/IFN/dasometricos/vegetacion.csv"
generalInfo = u"../data/IFN/informacion_general/informacion_general.csv"
coordenadas = u"../data/IFN/informacion_general/coordenadas.csv"
analizador = u"../data/IFN/suelos/analizador.csv"
carbono = u"../data/IFN/suelos/carbono.csv"
fertilidad = u"../data/IFN/suelos/fertilidad.csv"

# Leer archivos como Pandas dataframes
det = pd.read_csv(detritos, encoding = 'utf8') 
amp = pd.read_csv(ampie, encoding = 'utf8')
veg = pd.read_csv(vegetacion, encoding = 'utf8')
info = pd.read_csv(generalInfo, encoding = 'utf8')
coord = pd.read_csv(coordenadas, encoding = 'utf8')
analiz = pd.read_csv(analizador, encoding = 'utf8')
carb = pd.read_csv(carbono, encoding = 'utf8')
fert = pd.read_csv(fertilidad, encoding = 'utf8')


# # Analizador

# In[ ]:


CONS = u"CONS" # Indice analisis (int64)
PLOT = u"PLOT" # Indice conglomerado (int64)
SPF = u"SPF" # Indice subparcela (int64)
N = u"N" # Porcentaje de nitrogeno (float64: 0.0-100.0)
C = u"C" # Porcentaje de carbono (float64: 0.0-100.0)


# In[ ]:


logbuffer = u"\n" + u"#" * 50 + u"\nTABLA ANALIZADOR\n"

# Verificacion de tipo de datos

for fi in [CONS, PLOT, SPF]:
    if analiz[fi].dtype != np.int64:
        logbuffer += u"\nCampo {0} tiene tipo inapropiado ({1} en vez de int64).\n".format(fi,
                        analiz[fi].dtype)

        
for fi in [N, C]:
    if analiz[fi].dtype != np.float64:
        logbuffer += u"\nCampo {0} tiene tipo inapropiado ({1} en vez de float64).\n".format(fi,
                        analiz[fi].dtype)

if interactive:
    print logbuffer    
    logbuffer = u""


# In[ ]:


# Indices no debe contener duplicado
if len(analiz[analiz[CONS].duplicated()]):
    logbuffer += u"\nTabla {0} contiene indices duplicados.\n".format(analizador)
    
spf_ind = analiz.groupby([PLOT, SPF]).size().reset_index()
if len(spf_ind[spf_ind[0] > 1]):
    logbuffer += u"\nTabla {0} contiene pares Parcela-Subparcela duplicados.\n".format(analizador)

# Valores faltantes Parcela o Subparcela
if len(analiz[analiz[PLOT].isna()]):
    logbuffer += u"\nTabla {0} contiene datos faltantes de indice de parcela.\n".format(analizador)
    
if len(analiz[analiz[SPF].isna()]):
    logbuffer += u"\nTabla {0} contiene datos faltantes de indice de subparcela.\n".format(analizador)
    

for spf in analiz[SPF].dropna().unique():
    if spf not in [1,2,3,4,5]:
        logbuffer += u"\n`{0}` no es un valor valido de subparcela\n".format(spf)
        
if analiz[C].min() < 0 or analiz[N].min() < 0:
    logbuffer += u"\nValores mínimos de contenido de carbono o nitrogeno inferiores a lo permitido\n"
        
if analiz[C].max() > 100.0 or analiz[N].max() > 100.0:
    logbuffer += u"\nValores máximos de contenido de carbono o nitrogeno superiores a lo permitido\n"
        
if interactive:
    print logbuffer 

else:
    with cd.open(logfile, mode='w', encoding="utf-8") as fhandle:
        fhandle.write(logbuffer)

logbuffer = u""


# # Carbono

# In[ ]:


CONS = u"CONS" # Indice analisis (int64) 
PLOT = u"PLOT" # Indice conglomerado (int64) 
SPF = u"SPF" # Indice subparcela (int64) 
C = u"C" # Porcentaje de carbono (float64) 
SUELO = u"SUELO" # Masa de suelo en gr (float64) 
RAIZ = u"RAIZ" # Diametro promedio aproximado de raices, probablemente en cm (float64). Parecen haber males digitaciones. 
ROCA = u"ROCA" # Diametro promedio aproximado de rocas, probablemente en cm (float64). Parecen haber males digitaciones. 
VOL = u"VOL" # Volumen en ml (float64) 
DENS = u"DENS" # Densidad en gr/ml (float64) 


# In[ ]:


logbuffer = u"\n" + u"#" * 50 + u"\nTABLA CARBONO\n"

# Verificacion de tipo de datos

for fi in [CONS, PLOT, SPF]:
    if carb[fi].dtype != np.int64:
        logbuffer += u"\nCampo {0} tiene tipo inapropiado ({1} en vez de int64).\n".format(fi,
                        carb[fi].dtype)

        
for fi in [C, SUELO, RAIZ, ROCA, VOL, DENS]:
    if carb[fi].dtype != np.float64:
        logbuffer += u"\nCampo {0} tiene tipo inapropiado ({1} en vez de float64).\n".format(fi,
                        carb[fi].dtype)

if interactive:
    print logbuffer    
    logbuffer = u""


# In[ ]:


# Indices no debe contener duplicado
if len(carb[carb[CONS].duplicated()]):
    logbuffer += u"\nTabla {0} contiene indices duplicados.\n".format(carbono)
    
spf_ind = carb.groupby([PLOT, SPF]).size().reset_index()
if len(spf_ind[spf_ind[0] > 1]):
    logbuffer += u"\nTabla {0} contiene pares Parcela-Subparcela duplicados.\n".format(carbono)


for fi in [C, SUELO, RAIZ, ROCA, VOL, DENS]:
    if carb[fi].min() < 0:
        logbuffer += u"\nValor minimo de columna {0} no permitido.\n".format(fi)

    
##########################################################################################
# El manual del IFN no es claro respecto a las unidades o la forma en que se estima el 
# diametro promedio de raices y rocas. Aqui se asume que las unidades son cm y se eliminan
# todas aquellas con diametros superiores a 30 cm, la dimension basica de la excavacion
##########################################################################################
if len(carb[carb[RAIZ] > 30]):
    logbuffer += u"\nDiametro promedio de raiz superior a dimensiones de la excavacion.\n"
    
if len(carb[carb[ROCA] > 30]):

    logbuffer += u"\nDiametro promedio de roca superior a dimensiones de la excavacion.\n"

    logbuffer += carb[carb[ROCA] > 30][[PLOT, SPF, ROCA]].merge(info[[PLOT, u"SOCIO"]], on = PLOT
                    ).to_string(index = False) + u"\n"
    
    carb.drop(carb[carb[ROCA] > 30].index, inplace = True)
    
##########################################################################################
# De acuerdo al manual el volumen deberia ser siempre el mismo: 2.54**2 * 10 = 203.80 cm
##########################################################################################

if len(carb[(carb[DENS] - carb[SUELO] / carb[VOL]) > 0.001]):
    logbuffer += u"\nDensidad del suelo incorrectamente estimada.\n"

if interactive:
    print logbuffer 

else:
    with cd.open(logfile, mode='w', encoding="utf-8") as fhandle:
        fhandle.write(logbuffer)

logbuffer = u""


# # Fertilidad

# In[ ]:


CONS = u"CONS" # Indice de la medicion (int64).
PLOT = u"PLOT" # Indice conglomerado (int64).
pH = u"pH" # Acidez muestra (float64)
MO = u"MO" # Porcentaje de materia organica (float64)
P = u"P" # Contenido de fosforo en ppm (float64)
Al = u"Al" # Contenido de aluminio en meq (float64)
Ca = u"Ca" # Contenido de calcio en meq (float64)
Mg = u"Mg" # Contenido de magnesio en meq (float64)
K = u"K" # Contenido de potasio en meq (float64)
CICE = u"CICE" # Capacidad de intercambio cationico efectiva en meq (float64)
A = u"A" # Porcentaje de arena (int64)
L = u"L" # Porcentaje de limo (int64)
Ar = u"Ar" # Porcentaje de arena (int64)
TEXTURA = u"TEXTURA" # (str)
Cu = u"Cu" # Contenido de cobre en ppm (float64)
Fe = u"Fe" # Contenido de hierro en ppm (float64)
Mn = u"Mn" # Contenido de manganesio en ppm (float64)
Zn = u"Zn" # Contenido de zinc en ppm (float64)
N = u"N" # Porcentaje de nitrogeno (float64)


# In[ ]:


logbuffer = u"\n" + u"#" * 50 + u"\nTABLA FERTILIDAD\n"

# Verificacion de tipo de datos

for fi in [CONS, PLOT]:
    if fert[fi].dtype != np.int64:
        logbuffer += u"\nCampo {0} tiene tipo inapropiado ({1} en vez de int64).\n".format(fi,
                        fert[fi].dtype)

        
for fi in [MO, A, Ar, L, pH, CICE, Al, Ca, Cu, Fe, K, Mg, Mn, N, P, Zn]:
    if fert[fi].dtype != np.float64:
        logbuffer += u"\nCampo {0} tiene tipo inapropiado ({1} en vez de float64).\n".format(fi,
                        fert[fi].dtype)
        
for fi in [TEXTURA]:
    non_unicode = fert[fi].dropna()[~fert[fi].dropna().apply(type).eq(unicode)]
    if len(non_unicode):
        logbuffer += u"\nCampo {0} tiene tipo inapropiado ({1} en vez de unicode).\n".format(fi,
                        non_strings.dtype)


if interactive:
    print logbuffer    
    logbuffer = u""


# In[ ]:


# Indices no debe contener duplicado
if len(fert[fert[CONS].duplicated()]):
    logbuffer += u"\nTabla {0} contiene indices duplicados.\n".format(fertilidad)

for fi in [MO, A, Ar, L, pH, N]:
    if fert[fi].min() < 0:
        logbuffer += u"\nValor mínimo de campo {0} afuera del rango aceptado\n".format(fi)
    if fert[fi].max() > 100:
        logbuffer += u"\nValor máximo de campo {0} afuera del rango aceptado\n".format(fi)

# Valores textura de suelo
fert[TEXTURA] = fert[TEXTURA].str.upper()

myte = [u"A", u"AR", u"L", u"F", u"FA", u"FAR", u"FL", u"ARA", u"ARL", u"FARA", u"FARL",
        u"NO DISPERSA"]

for elem in fert[TEXTURA].unique():
    bits = elem.split(u"-")
    for b in bits:
        if b not in myte:
            logbuffer += u"\n`{0}` no es un valor aceptado de Textura de suelo.\n".format(b)
        
        
if interactive:
    print logbuffer 

else:
    with cd.open(logfile, mode='w', encoding="utf-8") as fhandle:
        fhandle.write(logbuffer)

logbuffer = u""


# # Detritos

# In[ ]:


# Campos de mediciones de detritos

CONS = u"CONS" # Indice de medicion (int64)
PLOT = u"PLOT" # Indice conglomerado (int64)
TRAN = u"TRAN" # Transecto de detritos (str: 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'). Hay registros sin transectos!!!
SECC = u"SECC" # Seccion del transecto donde se registro la pieza (str: 'II', 'III', 'I'). Hay registros sin seccion!!!!
PIEZA = u"PIEZA" # Numero consecutivo de la pieza en el transecto (float64). Deberia ser int64.
TIPO = u"TIPO" # Tipo de detrito (str: 'DFM', 'DGM')
DIST = u"DIST" # Distancia del detrito en cada seccion (float64 0.0-10.0)
AZIMUT = u"AZIMUT" # Orientacion de la pieza respecto al transecto ?????????? (float64?, 0-360)
D1 = u"D1" # Primer diametro de la pieza en cm (float64)
D2 = u"D2" # Segundo diametro de la pieza en cm (float64)
INCL = u"INCL" # Inclinacion de la pieza (float64). De acuerdo al manual deberia estar en el rango [-90, 90] pero en la hoja de calculo esta sesgada a valores positivos y hay valores [90, 180].
PI_cm = u"PI_cm" # Penetracion del penetrometro en cm (float64). Verificar valores maximos.
PI_golpes = u"PI_golpes" # Golpes ejecutados con el penetrometro (float64). Por que es un numero real????
PESO_RODAJA = u"PESO_RODAJA" # Peso de la rodaja en gr (float64)
ESP1 = u"ESP1" # Primer espesor de la rodaja en cm (float64)
ESP2 = u"ESP2" # Segundo espesor de la rodaja en cm (float64)
ESP3 = u"ESP3" # Tercer espesor de la rodaja en cm (float64)
ESP4 = u"ESP4" # Cuarto espesor de la rodaja en cm (float64)
PESO_MUESTRA = u"PESO_MUESTRA" # Peso fresco de la muestra en gr (float64)
VOL = u"VOL" # Volumen de la muestra en ml (float64). Este campo no esta incluido en los formatos del INF!!!!
PESO_SECO = u"PESO_SECO" # Peso fresco de la muestra en gr (float64)
DENS = u"DENS" # Densidad de madera de la muestra en gr/ml (float64)


# In[ ]:


logbuffer = u"\n" + u"#" * 50 + u"\nTABLA DETRITOS\n"

# Convertir seccion muestreo de detritos a int64 para ahorrar espacio en memoria
try:
    det[SECC].replace(to_replace = [u'I',u'II',u'III'], value = [1,2,3], inplace = True)
    # Si no existieran valores faltantes el reemplazo produciria una serie de int64, 
    # de lo contrario la columna resultante es float64
except:
    pass

for fi in [CONS, PLOT, SECC]:
    if det[fi].dtype != np.int64:
        logbuffer += u"\nCampo {0} tiene tipo inapropiado ({1} en vez de int64).\n".format(fi,
                        det[fi].dtype)
        if len(det[fi][det[fi].isna()]) > 1:
            logbuffer += u"\nValores nulos son considerados np.float64:\n"
            logbuffer += det[[CONS, fi, PLOT, TRAN]][det[fi].isna()].join(info[[u'PLOT', u'SOCIO']
                            ].set_index(PLOT), on=PLOT, rsuffix=u'_info').to_string(index=False) \
                            + "\n"
        else:
            logbuffer += u"\nValores np.float64 a revisar:\n"
            logbuffer += det[fi][det[fi].map(lambda x: x % 1.0 != 0)].dropna().to_string() + "\n"
        
for fi in [AZIMUT, PIEZA, DIST, D1, D2, INCL, PI_cm, PESO_RODAJA, ESP1, ESP2, ESP3, ESP4, 
           PESO_MUESTRA, VOL, PESO_SECO, DENS, PI_golpes]:
    if det[fi].dtype != np.float64:
        logbuffer += u"\nCampo {0} tiene tipo inapropiado ({1}en vez de float64).\n".format(fi,
                        det[fi].dtype)

for fi in [TRAN, TIPO]:
    non_unicode = det[fi].dropna()[~det[fi].dropna().apply(type).eq(unicode)]
    if len(non_unicode):
        logbuffer += u"\nCampo {0} tiene tipo inapropiado ({1} en vez de unicode).\n".format(fi,
                        non_strings.dtype)

if interactive:
    print logbuffer    
    logbuffer = u""


# In[ ]:


########################################################
# Para arreglar
# - ¿Que hacer con detritos con variabilidad excesiva 
#   en los espesores de rodaja?
#
########################################################

# Indices no debe contener duplicado
if len(det[det[CONS].duplicated()]):
    logbuffer += u"\nTabla {0} contiene indices duplicados.\n".format(detritos)
        
if len(det[det[TRAN].isna()]):
    
    logbuffer += u"\nPiezas de detritos no tienen transecto:\n"
    
    logbuffer += det[[CONS, PLOT, TRAN]][det[TRAN].isna()].join(info[[u'PLOT', u'SOCIO'
                    ]].set_index(PLOT), on=PLOT, rsuffix=u'_info').to_string(index= False) + "\n"
    
    # Piezas sin datos de transecto son eliminadas
    det.drop(det[det[TRAN].isna()].index, inplace=True)
        
for tr in det[TRAN].dropna().unique():
    if tr not in [u'A', u'B', u'C', u'D', u'E', u'F', u'G', u'H']:
        logbuffer += u"\n`{0}` no es un valor valido de transecto de detrito\n".format(tr)
        
for tr in det[SECC].dropna().unique():
    if tr not in [1,2,3]:
        logbuffer += u"\n`{0}` no es un valor valido de transecto de detrito\n".format(tr)

for tr in det[TIPO].dropna().unique():
    if tr not in [u'DFM', u'DGM']:
        logbuffer += u"\n`{0}` no es un valor valido de tipo de detrito\n".format(tr)
        
#############################################################################################
# Antes de verificar la asignacion del tipo de detrito los diámetros observados
# iguales a cero son declarados como datos faltantes
#############################################################################################
det.loc[det[D1] == 0, D1] = np.nan
det.loc[det[D2] == 0, D2] = np.nan
        
if len(det[(det[TIPO] == u'DFM') & (((det[D1] >= 20) & (det[D2].isna())) | (det[D1] + det[D2] >= 
        40))]):
    
    ###########################################################################
    # Tipo de detrito es reasignado de acuerdo al diametro registrado
    ###########################################################################
    logbuffer += u"\nTipo de detrito probablemente mal asignado:\n"

    logbuffer += det[[CONS, TIPO, D1, D2, PLOT, TRAN]][(det[TIPO] == u'DFM') & (((det[D1] >= 20) 
                    & (det[D2].isna())) | (det[D1] + det[D2] >= 40))].join(info[[u'PLOT', 
                    u'SOCIO']].set_index(PLOT), on=PLOT, rsuffix=u'_info').to_string(index = 
                    False) + "\n"
    
    det.loc[(det[TIPO] == u'DFM') & (((det[D1] >= 20) & (det[D2].isna())) | (det[D1] + det[D2] >= 40)
        ), TIPO] = u'DGM'

if len(det[(det[TIPO] == u'DGM') & (((det[D1] < 20) & (det[D2].isna())) | (det[D1] + det[D2] < 40))]):
    
    logbuffer += u"\nTipo de detrito probablemente mal asignado:\n"
    
    logbuffer += det[[CONS, TIPO, D1, D2, PLOT, TRAN]][(det[TIPO] == u'DGM') & (((det[D1] < 20) 
                    & (det[D2].isna())) | (det[D1] + det[D2] < 40))].join(info[[u'PLOT', 
                    u'SOCIO']].set_index(PLOT), on=PLOT, rsuffix=u'_info').to_string(index = 
                    False) + "\n"
    
    det.loc[(det[TIPO] == u'DGM') & (((det[D1] < 20) & (det[D2].isna())) | (det[D1] + det[D2] < 40)),
            TIPO] = u'DFM'

if det[DIST].min() < 0:
    logbuffer += u"\nRango distancia tiene valores negativos.\n"
    
if det[DIST].max() > 10:
    
    logbuffer += u"\nRango distancia sobrepasa el valor permitido (10).\n"
    
    logbuffer += det[[CONS, DIST, PLOT, TRAN]][det[DIST] > 10].join(info[[u'PLOT', u'SOCIO']
                    ].set_index(PLOT), on=PLOT, rsuffix=u'_info').to_string(index=False) + "\n"
    
    
    #############################################################################################
    # Al parecer las medidas de distancia de DFM menores a 9 realmente fueron realizadas con el 
    # punto de referencia adecuado. Teoricamente la zona de la seccion a ser considerada para
    # DFM fue modificada a lo largo de la ejecucion del proyecto.
    #
    # Correcciones de distancias mayores a 10 
    # Al parecer las medidas mayores a 10 m y menores a 30 m 
    # fueron realizadas sin reestablecer el punto de 
    # referencia al inicio de las secciones 2 y 3.
    #############################################################################################

    det.loc[(det[DIST] > 10) & (det[DIST] <= 20), SECC] = 2
    
    det.loc[(det[DIST] > 10) & (det[DIST] <= 20), DIST] = det[(det[DIST] > 10) & (det[DIST] <= 20)
        ][DIST] - 10

    det.loc[(det[DIST] > 20) & (det[DIST] <= 30), SECC] = 3
    
    det.loc[(det[DIST] > 20) & (det[DIST] <= 30), DIST] = det[(det[DIST] > 20) & (det[DIST] <= 30)
        ][DIST] - 20

    ##############################################
    # Se supone que las distancias mayores a 30 fueron 
    # erroneamente multiplicadas por 10
    ##############################################
    det.loc[det[DIST] > 30, DIST] = det[det[DIST] > 30][DIST] / 10

if len(det[(det[TIPO] == u'DFM') & (det[DIST] > 1) & (det[DIST] < 9)]):
    
    logbuffer += u"\nDetritos finos contienen valores no permitidos de distancia:\n"
    
    logbuffer += det[[CONS, TIPO, DIST, PLOT, TRAN]][(det[TIPO] == u'DFM') & (det[DIST] > 1)
                    & (det[DIST] < 9)].join(info[[u'PLOT', u'SOCIO']].set_index(PLOT), on=PLOT, 
                    rsuffix=u'_info').to_string(index = False) + "\n"
    
    ############################################################################################
    # Estos datos son eliminados, su inclusion en los analisis implican una subestimacion de la
    # densidad de detritos. 
    ############################################################################################
    det.drop(det[(det[TIPO] == u'DFM') & (det[DIST] > 1) & (det[DIST] < 9)].index, inplace= True)

if det[AZIMUT].min() < 0:
    logbuffer += u"\nRango Azimut tiene valores negativos.\n"
    
if det[AZIMUT].max() > 360:
    logbuffer += u"\nRango Azimut sobrepasa el valor permitido (360)\n"

#####################################################
# Valores dudosos de diametro
# Valores de diametro 0.0 no tratados como nulos
#####################################################
det[D2].replace(to_replace = 0.0, value = np.nan, inplace = True)

if len(det[(det[D1] + det[D2]) < 4]):
    logbuffer += u"\nRango de diametro tiene valores inferiores a 2 cm.\n"
    logbuffer += det[[CONS, D1, D2, PLOT, TRAN]][(det[D1] + det[D2]) < 4].join(info[[
                    u'PLOT', u'SOCIO']].set_index(PLOT), on=PLOT, rsuffix=u'_info').to_string(
                    index=False) + "\n"
    #####################################################
    # Detritos con diametro menor a 2 cm son eliminados
    #####################################################
    det.drop(det[(det[D1] + det[D2]) < 4].index, inplace=True)
    
if det[INCL].min() < -90:
    
    logbuffer += u"\nRango inclinacion tiene valores menores al valor permitido (-90).\n"
    
    logbuffer += det[[CONS, INCL, PLOT, TRAN]][det[INCL] < -90].join(info[[u'PLOT', u'SOCIO']
                    ].set_index(PLOT), on=PLOT, rsuffix=u'_info').to_string(index=False) + "\n"
    
if det[INCL].max() > 90:
    
    logbuffer += u"\nRango inclinacion sobrepasa el valor permitido (90)\n"
    
    logbuffer += det[[CONS, INCL, PLOT, TRAN]][det[INCL] > 90].join(info[[u'PLOT', u'SOCIO']
                    ].set_index(PLOT), on=PLOT, rsuffix=u'_info').to_string(index=False) + "\n"
    
    #################################################################
    # si los valores son mayores a 90 y menores a 180 se substrae 90
    #################################################################
    det.loc[(det[INCL] > 90) & (det[INCL] <= 180), INCL] = det.loc[(det[INCL] > 90) & (det[INCL] <=
                                                                    180), INCL] - 90.0
    

############################################################
############################################################
#
#                      PENETROMETRO
#
############################################################
############################################################
if len(det[(det[TIPO] == u"DFM") & (det[PI_cm].notna() | det[PI_golpes].notna())]):
    
    logbuffer += u"\nDetritos finos de madera con datos de penetrometro:\n"
    
    logbuffer += det[(det[TIPO] == u"DFM") & (det[PI_cm].notna() | det[PI_golpes].notna())][[CONS,
                    D1, D2, PI_cm, PI_golpes, PLOT]].merge(info[[u"PLOT", u"SOCIO"]], on=
                    PLOT).to_string(index=False) + u"\n"
    
    # Datos de penetrometro de DFM son eliminados
    det.loc[(det[TIPO] == u"DFM") & det[PI_cm].notna(), PI_cm] = np.nan
    det.loc[(det[TIPO] == u"DFM") & det[PI_golpes].notna(), PI_golpes] = np.nan

if len(det[PI_cm][(det[PI_cm] > det[D1]) | (det[PI_cm] > det[D2])]):
    
    logbuffer += u"\nValores de entrada del penetrometro son mayores al diametro registrado:\n"
    
    logbuffer += det[[CONS, PI_cm, D1, D2, PLOT, TRAN]][(det[PI_cm] > det[D1]) | (det[PI_cm] 
                    > det[D2])].join(info[[u'PLOT', u'SOCIO']].set_index(PLOT), on=PLOT, 
                    rsuffix=u'_info').to_string(index=False) + "\n"
    
    ############################################################################
    # Registros eliminados si la entrada del penetrometro es mayor al diametro
    ###########################################################################
    det.drop(det[(det[PI_cm] > det[D1]) | (det[PI_cm] > det[D2])].index, inplace=True)
    
    
if det[PI_golpes].min() < 0:
    logbuffer += u"\nValores negativos de golpes al penetrometro.\n"

    
if len(det[(det[PI_golpes] == 0) & (det[PI_cm] > 0)]):
    
    logbuffer += u"\nRegistros con medida de penetrometro pero cero golpes:\n"
    
    logbuffer += det[(det[PI_golpes] == 0) & (det[PI_cm] > 0)][[CONS, PLOT, TRAN, PI_cm, 
                    PI_golpes]].merge(info[[u"PLOT", u"SOCIO"]], on=PLOT).to_string(index =
                    False) + u"\n"
    
    # Se asume que los 20 golpes obligatorios fueron realizados
    det.loc[(det[PI_golpes] == 0) & (det[PI_cm] > 0), PI_golpes] = 20

    
if len(det[(det[PI_golpes] % 1 != 0) & det[PI_golpes].notna() & (det[PI_cm].isna() | (det[PI_cm]
        == 0))]):

    logbuffer += u"\nNúmero de golpes fueron consignados como numeros reales, no enteros:\n"
    
    logbuffer += det[(det[PI_golpes] % 1 != 0) & det[PI_golpes].notna() & (det[PI_cm].isna()
                    | (det[PI_cm] == 0))][[CONS, PI_golpes, PI_cm, PLOT]].merge(info[[u"PLOT", 
                    u"SOCIO"]], on = PLOT, ).to_string(index = False) + u"\n"

    # Se asume que dichas medidas corresponden a cm de penetracion despues de realizar los 20 
    # golpes obligatorios
    det.loc[((det[PI_golpes] % 1 != 0) & det[PI_golpes].notna() & (det[PI_cm].isna() | (det[PI_cm] 
            == 0))), PI_cm] = det[(det[PI_golpes] % 1 != 0) & det[PI_golpes].notna()
            & (det[PI_cm].isna() | (det[PI_cm] == 0))][PI_golpes]
    
    det.loc[((det[PI_golpes] % 1 != 0) & det[PI_golpes].notna() & (det[PI_cm].isna() | (det[PI_cm] 
            == 0))), PI_golpes] = 20

    
if len(det[(det[PI_cm] < 20) & (det[PI_golpes] < 20) & (det[PI_golpes] == det[PI_cm])]):
    
    logbuffer += u"\nNumero de golpes de penetrómeto y profundidad de entrada son iguales y "         + u"menores a 20:\n"
    
    logbuffer += det[(det[PI_cm] < 20) & (det[PI_golpes] < 20) & (det[PI_golpes] == det[PI_cm])][[
        CONS, PI_cm, PI_golpes, PLOT]].merge(info[[u"PLOT", U"SOCIO"]], on = PLOT).to_string(
        index = False) + u"\n"
    
    # Se asume que los datos de profundidad de entrada de pénetrometro estan duplicados en la
    # columna de No. golpes y que el No. de golpes realizado fue 20
    det.loc[(det[PI_cm] < 20) & (det[PI_golpes] < 20) & (det[PI_golpes] == det[PI_cm]), PI_golpes]         = 20

        
if len(det[(det[PI_golpes] < 20) & det[PI_cm].notna()]):
    logbuffer += u"\nValores de profundidad de entrada del penetrometro no son NaN aunque se "         + u"realizaron menos de 20 golpes:\n"
        
    logbuffer += det[(det[PI_golpes] < 20) & det[PI_cm].notna()][[CONS, PI_cm, PI_golpes, PLOT]
                    ].merge(info[[u"PLOT", u"SOCIO"]], on=PLOT).to_string(index=False) + u"\n"

    
if det[PI_golpes].max() > 20:
    
    logbuffer += u"\nValores de golpes del penetrometro mayores a lo permitido (20):\n"
    
    logbuffer += det[[CONS, PI_golpes, PLOT, TRAN]][det[PI_golpes] > 20].join(info[[u'PLOT', 
                    u'SOCIO']].set_index(PLOT), on=PLOT, rsuffix=u'_info').to_string(index = 
                    False) + "\n"
    
    # Se asume que son mediciones de entrada de penetrometro si dicha medida es ausente 
    # y la medida es inferior a uno de los diametros. Tambien se asume que se ejecutaron
    # los 20 golpes obligatorios
    det.loc[(det[PI_golpes] > 20) & (det[PI_cm].isna() | (det[PI_cm] == 0)) & ((det[PI_golpes]
        < det[D1]) | (det[PI_golpes] < det[D2])), PI_cm] = det[(det[PI_golpes] > 20) & 
        (det[PI_cm].isna() | (det[PI_cm] == 0)) & ((det[PI_golpes] < det[D1]) | (det[PI_golpes] 
        < det[D2]))][PI_golpes]
    
    det.loc[(det[PI_golpes] > 20) & ((det[PI_golpes] < det[D1]) | (det[PI_golpes] < det[D2])),
        PI_golpes] = 20
    

if det[PI_cm].min() < 0:
    logbuffer += u"\nHay valores negativos de entrada del penetrometro.\n"
    
if det[PI_cm].max() > 20:
    
    logbuffer += u"\nValores maximos del entrada del penetrometro mayores al valor sugerido en el manual:\n"
    
    logbuffer += det[[CONS, PI_cm, PLOT, TRAN]][det[PI_cm] > 20].join(info[[u'PLOT', u'SOCIO']
                    ].set_index(PLOT), on=PLOT, rsuffix=u'_info').to_string(index=False) + "\n"
    
    det.loc[det[PI_cm] > 20 , PI_cm] = 20


# De acuerdo al manual, cuando se toman datos de penetrómetro se deben registrar tanto
# la profundidad como el numero de golpes. Por lo tanto, registros con datos faltantes
# en cualquiera de estos dos casos son considerados como valores maximos (20)
det.loc[(det[PI_golpes].isna() & det[PI_cm].notna()), PI_golpes] = 20
det.loc[(det[PI_golpes].notna() & det[PI_cm].isna()), PI_cm] = 20


# Sets de valores de espesor de pieza son dudosos si la desviacion estandar es mayor a 0.3 
# la media del set
if len(det[(det[[ESP1, ESP2, ESP3, ESP4]].std(1) / det[[ESP1, ESP2, ESP3, ESP4]].mean(1)) > 0.3]):
    
    logbuffer += u"\nAlgunos conjuntos de espesor de pieza tienen una variacion muy alta:\n"
    
    logbuffer += det[[CONS, ESP1, ESP2, ESP3, ESP4, PLOT, TRAN]][(det[[ESP1, ESP2, ESP3, ESP4]
                    ].std(1) / det[[ESP1, ESP2, ESP3, ESP4]].mean(1)) > 0.3].join(info[[u'PLOT', 
                    u'SOCIO']].set_index(PLOT), on=PLOT, rsuffix=u'_info').to_string(index =
                    False) + "\n"
    
if len(det[(det[PESO_MUESTRA] < det[PESO_SECO]) | (det[PESO_MUESTRA].isna() & (det[PESO_RODAJA] < 
        det[PESO_SECO]))]):
    
    logbuffer += u"\nPeso fresco es menor al peso seco o ausente:\n"

    logbuffer += det[[CONS, PESO_MUESTRA, PESO_RODAJA, PESO_SECO, PLOT, TRAN]][(det[PESO_MUESTRA] 
                    < det[PESO_SECO]) | (det[PESO_MUESTRA].isna() & (det[PESO_RODAJA] < 
                    det[PESO_SECO]))].join(info[[u'PLOT', u'SOCIO']].set_index(PLOT), on=PLOT, 
                    rsuffix=u'_info').to_string(index = False) + "\n"
    
    # Se presume que los pesos fueron intercambiados
    indxs = det[(det[PESO_MUESTRA] < det[PESO_SECO]) & ((det[PESO_RODAJA] > det[PESO_SECO]) | 
                det[PESO_RODAJA].isna())].index
    temp = det.loc[indxs, PESO_MUESTRA]
    det.loc[indxs, PESO_MUESTRA] = det.loc[indxs, PESO_SECO]    
    det.loc[indxs, PESO_SECO] = temp
    
    #######################################################
    # Registros con peso seco mayor al seco son eliminados
    #######################################################
    #det.drop(det[(det[PESO_MUESTRA] < det[PESO_SECO]) | (det[PESO_MUESTRA].isna() &
    #    (det[PESO_RODAJA] < det[PESO_SECO]))].index, inplace=True)
    
if det[(det[PESO_MUESTRA] > det[PESO_RODAJA])].size:
    
    logbuffer += u"\nPeso del fragmento muestreado es mayor al de la rodaja:\n"
    
    logbuffer += det[[CONS, TIPO, PESO_MUESTRA, PESO_RODAJA, PESO_SECO, PLOT, TRAN]][
                    (det[PESO_MUESTRA] > det[PESO_RODAJA])].join(info[[u'PLOT', u'SOCIO']
                    ].set_index(PLOT), on=PLOT, rsuffix=u'_info').to_string(index=False) + "\n"
    
    # Intercambiar peso muestra y peso rodaja cuando el intercambio sea evidente
    temp = det[[PESO_MUESTRA, PESO_RODAJA]][(det[PESO_MUESTRA] > det[PESO_RODAJA]) & 
                (det[PESO_RODAJA] > det[PESO_SECO]) & (det[TIPO] == u"DGM")]
    
    det.loc[temp.index,PESO_MUESTRA] = temp[PESO_RODAJA]

    det.loc[temp.index,PESO_RODAJA] = temp[PESO_MUESTRA]
    
    #############################################################################################
    # Las restantes incongruencias corresponden a detritos finos de madera seccionados en rodajas
    # ¿Por que se muestrearon de esa forma? ¿Los diametros son correctos?
    # No es posible aclarar el origen del problema sin analizar los formatos directamente.
    # Registros eliminados
    #############################################################################################
    det.drop(det[(det[PESO_MUESTRA] > det[PESO_RODAJA])].index, inplace=True)
    
if det[det[PESO_MUESTRA].isna() & det[PESO_RODAJA].isna()].size:
    
    logbuffer += u"\nFalta peso fresco de detrito:\n"
    
    logbuffer += det[[CONS, TIPO, PESO_MUESTRA, PESO_RODAJA, PESO_SECO, PLOT, TRAN]][
                    det[PESO_MUESTRA].isna() & det[PESO_RODAJA].isna()].join(info[[u'PLOT', 
                    u'SOCIO']].set_index(PLOT), on=PLOT, rsuffix=u'_info').to_string(index
                    = False) + "\n"
    
    # Se predume que en algunos casos el peso fresco fue registrado en la casilla de  peso rodaja
    # Si la relacion entre peso rodaja y peso seco es menor a 10:1 se copia el peso rodaja a peso 
    # fresco
    det.loc[det[PESO_RODAJA].notna() & det[PESO_MUESTRA].isna() & det[PESO_SECO].notna() & 
        ((det[PESO_SECO] / det[PESO_RODAJA]) >= 0.1), PESO_MUESTRA] = det[det[PESO_RODAJA].notna() &
        det[PESO_MUESTRA].isna() & det[PESO_SECO].notna() & ((det.PESO_SECO / det.PESO_RODAJA) >= 0.1)
        ][PESO_RODAJA]
    
    # Restantes registros sin peso de fresco son eliminados
    det.drop(det[det[PESO_MUESTRA].isna()].index, inplace=True)
    
    
if len(det[det[PESO_SECO].isna()]):
    
    logbuffer += u"\nFalta peso seco de detrito:\n"
    
    logbuffer += det[[CONS, TIPO, PESO_MUESTRA, PESO_RODAJA, PESO_SECO, PLOT, TRAN]][
                    det[PESO_SECO].isna()].join(info[[u'PLOT', u'SOCIO']].set_index(PLOT), 
                    on=PLOT, rsuffix=u'_info').to_string(index=False) + "\n"
    
    det.drop(det[det[PESO_SECO].isna()].index, inplace=True)
    
if interactive:
    print logbuffer 
    pass
else:
    with cd.open(logfile, mode='w', encoding="utf-8") as fhandle:
        fhandle.write(logbuffer)

logbuffer = u""


# # Vegetacion

# In[ ]:


CONS = u"CONS" # Indice de medicion comun con arboles muertos en pie (int)
PLOT = u"PLOT" # Indice conglomerado (int)
SPF = u"SPF" # Indice subparcela (int 1-5)
IND = u"IND" # Indice de individuo en el conglomerado (int)
TAMANO = u"TAMANO" # Tamaño del individuo (str: 'L', 'F', o 'FG')
AZIMUT = u"AZIMUT" # Orientacion del individuo desde el centro de la subparcela (int, 0-360)
DIST = u"DIST" # Distancia en m del individuo al centro de la parcela (float, 0-15.74)
DAP1 = u"DAP1" # Primer diámetro estimado del tallo en cm (float)
DAP2 = u"DAP2" # Segundo diámetro estimado del tallo en cm (float)
DAPA = u"DAPA" # Diametro promedio del tallo en cm (float)
ALTF = u"ALTF" # Altura fuste en m (float)
ALTT = u"ALTT" # Altura total en m (float)
FAMILIA = u"FAMILIA" # Familia taxonomica (str)
GENERO = u"GENERO" # Genero taxonomico (str)
EPITETO = u"EPITETO" # Epiteto taxonomico (str)
AUTOR = u"AUTOR" # Autor taxonomico (str)
ESPECIE = u"ESPECIE" # Binomio taxonomico (str)
DENS = u"DENS" # Densidad de la madera en gr/ml (float)
FUENTE_DENSIDAD = u"FUENTE_DENSIDAD" # Referencia bibliografica de la densidad de la madera (str)


# In[ ]:


logbuffer = u"\n" + u"#" * 50 + u"\nTABLA VEGETACION\n"
for fi in [CONS, PLOT, SPF, IND]:
    if veg[fi].dtype != np.int64:
        logbuffer += u"\nCampo {0} tiene tipo inapropiado ({1} en vez de int64).\n".format(fi, veg[fi].dtype)
        if len(veg[fi][det[fi].isna()]) > 1:
            logbuffer += u"\nValores nulos son considerados np.float64:\n"
            logbuffer += veg[[CONS, fi, PLOT, SPF]][veg[fi].isna()].join(info[['PLOT',
                            'SOCIO']].set_index(PLOT), on=PLOT, rsuffix='_info').to_string(
                            index = False) + "\n"
        else:
            logbuffer += u"\nValores np.float64 a revisar:\n"
            logbuffer += veg[CONS, fi, PLOT, SPF][veg[fi].map(lambda x: x % 1.0 != 0)].dropna(
                            ).merge(info[['PLOT', 'SOCIO']], on=PLOT).to_string(index = False
                            ) + "\n"
            
        
for fi in [AZIMUT, DIST, DAP1, DAP2, DAPA, ALTT, ALTF, DENS]:
    if veg[fi].dtype != np.float64:
        logbuffer += u"\nCampo {0} tiene tipo inapropiado ({1}en vez de float64).\n".format(fi, veg[fi].dtype)

for fi in [FAMILIA, GENERO, EPITETO, AUTOR, ESPECIE, FUENTE_DENSIDAD, TAMANO]:
    non_strings = veg[fi].dropna()[~veg[fi].dropna().apply(type).eq(unicode)]
    if len(non_strings):
        logbuffer += u"\nCampo {0} tiene tipo inapropiado ({1} en vez de unicode).\n".format(fi, non_strings.dtype)

if interactive:
    print logbuffer 
    logbuffer = u""


# In[ ]:


if len(veg[veg[CONS].duplicated()]):
    logbuffer += u"\nTabla {0} contiene indices duplicados.\n".format(vegetacion)

for spf in veg[SPF].unique():
    if spf not in range(1,6):
        logbuffer += u"\nValor no valido de parcela: {0}\n".format(spf)
        
for tam in veg[TAMANO].unique():
    if tam not in [u'B', u'L', u'F', u'FG']:
        logbuffer += u"\nValor no valido de tamaño de individuo: {0}\n".format(tam)
        
if veg[AZIMUT].min() < 0:
    logbuffer += u"\nAzimut contiene valores no aceptados.\n"

if veg[AZIMUT].max() > 360:
    logbuffer += u"\nAzimut contiene valores no aceptados.\n"
    
# Verificar asignacion de clases diametricas
if len(veg[(veg[TAMANO] != u'B') & ((veg[DAPA] < 2.5) | ((veg[DAP1] + veg[DAP2]) < 5.0))]):

    logbuffer += u"\nBrinzales están asignados a categoria erronea:\n"

    logbuffer += veg[[CONS, PLOT, SPF, TAMANO, DAPA, DAP1, DAP2]][(veg[TAMANO] != u'B') 
                    & ((veg[DAPA] < 2.5) | ((veg[DAP1] + veg[DAP2]) < 5.0))].join(
                    info[[u'PLOT', u'SOCIO']].set_index(PLOT), on=PLOT, rsuffix = 
                    u'_info').to_string(index=False) + "\n"

    veg.loc[(veg[TAMANO] != u'B') & ((veg[DAPA] < 2.5) | ((veg[DAP1] + veg[DAP2]) < 5.0)), 
        TAMANO] = u'B'
    
if len(veg[(veg[TAMANO] != u'L') & (((veg[DAPA] < 10) & (veg[DAPA] >= 2.5)) | (((veg[DAP1] + 
        veg[DAP2]) < 20) & ((veg[DAP1] + veg[DAP2]) >= 5.0)))]):
    
    logbuffer += u"\nLatizales están asignados a categoria erronea:\n"
    
    logbuffer += veg[[CONS, PLOT, SPF, TAMANO, DAPA, DAP1, DAP2]][(veg[TAMANO] != u'L') 
                    & (((veg[DAPA] < 10) & (veg[DAPA] >= 2.5)) | (((veg[DAP1] + veg[DAP2]) < 20) 
                    & ((veg[DAP1] + veg[DAP2]) >= 5.0)))].join(info[[u'PLOT', u'SOCIO']
                    ].set_index(PLOT), on=PLOT, rsuffix=u'_info').to_string(index= False
                    ) + "\n"
    
    veg.loc[(veg[TAMANO] != u'L') & (((veg[DAPA] < 10) & (veg[DAPA] >= 2.5)) | (((veg[DAP1] 
            + veg[DAP2]) < 20) & ((veg[DAP1] + veg[DAP2]) >= 5.0))), TAMANO] = u'L'
    
if len(veg[(veg[TAMANO] != u'F') & (((veg[DAPA] < 30) & (veg[DAPA] >= 10)) | (((veg[DAP1] + 
        veg[DAP2]) < 60) & ((veg[DAP1] + veg[DAP2]) >= 20)))]):
    
    logbuffer += u"\nFustales están asignados a categoria erronea:\n"
    
    logbuffer += veg[[CONS, PLOT, SPF, TAMANO, DAPA, DAP1, DAP2]][(veg[TAMANO] != u'F') 
                    & (((veg[DAPA] < 30) & (veg[DAPA] >= 10)) | (((veg[DAP1] + veg[DAP2]) < 60) 
                    & ((veg[DAP1] + veg[DAP2]) >= 20)))].join(info[[u'PLOT', u'SOCIO']
                    ].set_index(PLOT), on=PLOT, rsuffix=u'_info').to_string(index=False
                    ) + "\n"
    
    veg.loc[(veg[TAMANO] != u'F') & (((veg[DAPA] < 30) & (veg[DAPA] >= 10)) | (((veg[DAP1]
        + veg[DAP2]) < 60) & ((veg[DAP1] + veg[DAP2]) >= 20))) , TAMANO] = u'F'
    
if len(veg[(veg[TAMANO] != u'FG') & ((veg[DAPA] >= 30) | ((veg[DAP1] + veg[DAP2]) >= 60))]):
    
    logbuffer += u"\nFustales grandes están asignados a categoria erronea:\n"
    
    logbuffer += veg[[CONS, PLOT, SPF, TAMANO, DAPA, DAP1, DAP2]][(veg[TAMANO] != u'FG') 
                    & ((veg[DAPA] >= 30) | ((veg[DAP1] + veg[DAP2]) >= 60))].join(info[[u'PLOT', 
                    u'SOCIO']].set_index(PLOT), on=PLOT, rsuffix=u'_info').to_string(index=
                    False) + "\n"

# Verificar si las distancias corresponden a las categorias de edad.
# Latizales y Fustales afuera de su area de medición son eliminados
if len(veg[(veg[DIST] > 3) & (veg[TAMANO] == u'L')]):
    
    logbuffer += u"\nLatizales registrados afuera del area aceptada:\n"
    
    logbuffer += veg[[CONS, TAMANO, DIST, DAPA, PLOT, SPF]][(veg[DIST] > 3) & (veg[TAMANO] 
                    == u'L')].join(info[[u'PLOT', u'SOCIO']].set_index(PLOT), on=PLOT, 
                    rsuffix='_info').to_string(index=False) + "\n"
    
    veg.drop(veg[(veg[DIST] > 3) & (veg[TAMANO] == u'L')].index, inplace=True)
    
if len(veg[(veg[DIST] > 7) & (veg[TAMANO] == u'F')]):
    
    logbuffer += u"\nFustales registrados afuera del area aceptada:\n"
    
    logbuffer += veg[[CONS, TAMANO, DIST, DAPA, PLOT, SPF]][(veg[DIST] > 7) & (veg[TAMANO] 
                    == u'F')].join(info[[u'PLOT', u'SOCIO']].set_index(PLOT), on=PLOT, 
                    rsuffix=u'_info').to_string(index=False) + "\n"
    
    veg.drop(veg[(veg[DIST] > 7) & (veg[TAMANO] == u'F')].index, inplace=True)
    
if len(veg[veg[DIST] > 15]):
    
    logbuffer += u"\nIndividuos registrados afuera del area de la subparcela:\n"
    
    logbuffer += veg[[CONS, TAMANO, DIST, DAPA, PLOT, SPF]][veg[DIST] > 15].join(info[[u'PLOT', 
                    u'SOCIO']].set_index(PLOT), on=PLOT, rsuffix=u'_info').to_string(index=
                    False) + "\n"
    
    veg.drop(veg[veg[DIST] > 15].index, inplace = True)

# Verificar estimacion DAP promedio
if veg[((veg[DAP1] + veg[DAP2]) - (veg[DAPA] * 2)) > 0.1].size:
    
    logbuffer += u"\nErrores en la estimación del DAP promedio?:\n"
    
    logbuffer += veg[[CONS, DAPA, DAP1, DAP2, PLOT, SPF]][((veg[DAP1] + veg[DAP2]) - 
                    (veg[DAPA] * 2)) > 0.01].join(info[[u'PLOT', u'SOCIO']].set_index(PLOT),
                    on=PLOT, rsuffix=u'_info').to_string(index=False) + "\n"

# Altura total siempre debe ser mayor a la altura del fuste
if veg[veg[ALTF] > veg[ALTT]].size:
    
    logbuffer += u"\nIndividuos con altura del fuste mayor a la altura total:\n"
    
    logbuffer += veg[[CONS, ALTF, ALTT, PLOT, SPF]][veg[ALTF] > veg[ALTT]].join(info[[u'PLOT',
                    u'SOCIO']].set_index(PLOT), on = PLOT, rsuffix = u'_info').to_string(index
                    =False) + "\n"

# Verificar determinaciones incongruentes entre tallos de individuos multiples
indsppcount = veg.groupby([PLOT,SPF,IND, GENERO, EPITETO]).size().reset_index()
indcount = indsppcount.groupby([PLOT,SPF,IND]).size().reset_index().rename(columns={0:u'size'})
if len(indcount[indcount[u'size'] > 1]):
    
    logbuffer += u"\nIndividuos de tallos multiples con determinaciones de varias especies:\n"
    
    logbuffer += indcount[indcount[u'size'] > 1].merge(info[[u'PLOT', u'SOCIO']], on = PLOT
                    ).to_string(index = False) + u"\n"



if interactive:
    print logbuffer 
else:
    with cd.open(logfile, mode='a', encoding="utf-8") as fhandle:
        fhandle.write(logbuffer)
logbuffer = u""


# # Informacion general

# In[ ]:


CONS = u'CONS' # Indice informacion (int64)
PLOT = u'PLOT' # Indice conglomerado (int64)
DEPARTAMENTO = u'DEPARTAMENTO' # Departamento (str)
REGION = u'REGION' # Region biogeografica (str: 'Amazonia', 'Andes', 'Pacifico', 'Orinoquia', 'Caribe')
FECHA_CAMPO = u'FECHA_CAMPO' # Año de toma de datos (int64)
SOCIO = u'SOCIO' # Institucion que ejecuta el levantamiento de datos (str: 'Sinchi', 'IAvH', 'IIAP')
BOT_TOT = u'BOT_TOT' # ???????????????? (str: 'Si', 'No'). Deberia ser boolean.
CARB = u'CARB' # Estimacion de carbono ????? (str: 'Si', 'No'). Deberia ser boolean.
SPFC = u'SPF-C' # En cuantas parcelas se tomaron datos de carbono (int64 0-5)
FERT = u'FERT' # Estimacion fertilidad (str: 'Si', 'No'). Deberia ser boolean.
DETR = u'DETR' # Toma de detritos (str: 'Si', 'No'). Deberia ser boolean.


# In[ ]:


logbuffer = u"\n" + u"#" * 50 + u"\nTABLA INFORMACION GENERAL\n"
# Verificar el tipo de dato an cada campo de la tabla informacion general
for fi in [CONS, PLOT, FECHA_CAMPO, SPFC]:
    if info[fi].dtype != np.int64:
        logbuffer += u"\nCampo {0} tiene tipo inapropiado ({1} en vez de int64).\n".format(fi, veg[fi].dtype)
        if len(info[fi][det[fi].isna()]) > 1:
            logbuffer += u"\nValores nulos son considerados np.float64:\n"
            logbuffer += info[[fi, PLOT, SOCIO]][det[fi].isna()].to_string()
        else:
            logbuffer += u"\nValores np.float64 a revisar:\n"
            logbuffer += info[fi][info[fi].map(lambda x: x % 1.0 != 0)].dropna().to_string()
            
for fi in [DEPARTAMENTO, REGION, SOCIO]:
    non_strings = info[fi].dropna()[~info[fi].dropna().apply(type).eq(unicode)]
    if len(non_strings):
        logbuffer += u"\nCampo {0} tiene tipo inapropiado ({1} en vez de unicode).\n".format(fi, non_strings.dtype)

#########################################################
# Se asume que los campos BOT_TOT, fertilidad y detritos 
# son boolean en vez de texto
#########################################################
try:
    info[BOT_TOT].replace(to_replace = [u'Si', u'No'], value = [True, False], inplace = True)
    info[FERT].replace(to_replace = [u'Si', u'No'], value = [True, False], inplace = True)
    info[DETR].replace(to_replace = [u'Si', u'No'], value = [True, False], inplace = True)
    info[CARB].replace(to_replace = [u'Si', u'No'], value = [True, False], inplace = True)
except TypeError, ErrorMessage:
    if ErrorMessage.args[0] == "Cannot compare types 'ndarray(dtype=bool)' and 'unicode'":
        pass
except:
    raise
    
for fi in [BOT_TOT, DETR, FERT, CARB]:
    if info[fi].dtype != np.bool:
        logbuffer += u"\nCampo {0} tiene tipo inapropiado ({1} en vez de np.bool).\n".format(fi, veg[fi].dtype)
        
if interactive:
    print logbuffer 
    logbuffer = u""


# In[ ]:


# Verificar rango de datos
if len(info[info[CONS].duplicated()]):
    logbuffer += u"\nTabla {0} contiene indices duplicados.\n".format(generalInfo)

for spf in info[SPFC].unique():
    if spf not in range(1,6):
        logbuffer += u"\nValor no valido de parcela: {0}\n".format(spf)
        logbuffer += info[[PLOT, SPFC, SOCIO]][info[SPFC] == spf].to_string(index = False)
        info.drop(info[info[SPFC] == spf].index, inplace=True)

if len(info[info[DETR].isna() | info[CARB].isna() | info[BOT_TOT].isna() | info[FERT].isna()]):
    logbuffer += u"\nDatos faltantes en columna Detritos, Carbono, Fertilidad o BOT_TOT:\n"
    logbuffer += info[[DETR, CARB, BOT_TOT, FERT, PLOT, SPFC, SOCIO]][info[DETR].isna() | 
                    info[CARB].isna() | info[BOT_TOT].isna() | info[FERT].isna()].to_string(
                    index=False)
        
if interactive:
    print logbuffer 
else:
    with cd.open(logfile, mode='a', encoding="utf-8") as fhandle:
        fhandle.write(logbuffer)
logbuffer = u""


# # Árboles muertos en pie

# In[ ]:


CONS = u'CONS' # Indice de medicion comun con arboles en pie (int64)
PLOT = u'PLOT' # Indice conglomerado (int64)
SPF = u'SPF' # Indice subparcela (int64)
TAMANO = u'TAMANO' # Tamaño del individuo (str: 'L', 'F', o 'FG')
IND = u'IND' # Indice de individuo en el conglomerado (int64)
COND = u'COND' # Condicion del individuo (str, 'MP', 'TO', 'VP', 'MC', 'M'). Valores TO, MC y M no estan consignados en el manual del INF. Que hacen individuos vivos (VP) en esta tabla?????
AZIMUT = u'AZIMUT' # Orientacion del individuo desde el centro de la subparcela (int, 0-360)
DIST = u'DIST' # Distancia en m del individuo al centro de la parcela (float, 0-15.74)
DAP_EQUIPO = u'DAP_EQUIPO' # Equipo empleado en la medicion de DAP (str: 'CD', 'FO', 'CA', 'CM'). Cuales son CM y CD? No estan especificados en el manual del INF.
DAP1 = u'DAP1' # Primer diámetro estimado del tallo en cm (float64)
DAP2 = u'DAP2' # Segundo diámetro estimado del tallo en cm (float64)
DAPA = u'DAPA' # Diametro promedio del tallo en cm (float64)
POM = u'POM' # Punto de observacion de la medida en m (float64). Hay medidas en cm.
ALT_EQUIPO = u'ALT_EQUIPO' # Equipo usado en la medicion de la altura (str: 'HI', 'VT', 'CL', 'CM', 'VX', 'FL', 'CD'). Valores 'CM', 'VX', 'FL' y 'CD' no esta especificados en el manual del INF.???????????????????
ALTF = u'ALTF' # Altura fuste en m (float)
ALTT = u'ALTT' # Altura total en m (float)
FORMA_FUSTE = u'FORMA_FUSTE' # (str: 'CIL', 'RT','IRR','FA','HI','Q'). Clases de valores estan repetidos por insercion de espacios o uso de minusculas. Valores 'HI' y 'Q' no estan consignados en el manual del INF. ??????????
DANO = u'DANO' # Daño registrado (str: 'Q', 'DB', 'SD', 'DM', 'IRR', 'EB'). Valor 'IRR' no esta consignado en el manual del INF.?????
PI_cm = u'Pi_cm' # Penetracion del penetrometro en cm (float64).
PI_golpes = u'Pi_golpes' # Golpes ejecutados con el penetrometro (float64). Por que es un numero real????


# In[ ]:


logbuffer = u"\n" + u"#" * 50 + u"\nTABLA ARBOLES MUERTOS EN PIE\n"
for fi in [CONS, PLOT, SPF, IND, AZIMUT]:
    if amp[fi].dtype != np.int64:
        logbuffer += u"\nCampo {0} tiene tipo inapropiado ({1} en vez de int64).\n".format(
                        fi, amp[fi].dtype)
        if len(amp[fi][amp[fi].isna()]) > 1:
            logbuffer += u"\nLos siguentes valores nulos son considerados np.float64 por Pandas:\n"
            logbuffer += amp[[fi, PLOT, SPF]][amp[fi].isna()].merge(info[[PLOT, SOCIO]], 
                            on=PLOT, how='left').to_string(index=False)
        else:
            logbuffer += u"\nValores np.float64 a revisar:\n"
            logbuffer += amp[[fi, PLOT, SPF]][amp[fi].map(lambda x: x % 1.0 != 0)].dropna().merge(
                            info[[PLOT, SOCIO]], on=PLOT, how='left').to_string(index=False)
            
for fi in [DIST, DAP1, DAP2, DAPA, POM, ALTF, ALTT, PI_cm, PI_golpes]:
    if amp[fi].dtype != np.float64:
        logbuffer += u"\nCampo {0} tiene tipo inapropiado ({1} en vez de float64)\n.".format(
                        fi, amp[fi].dtype)
        
        
for fi in [TAMANO, COND, DAP_EQUIPO, ALT_EQUIPO, FORMA_FUSTE, DANO]:
    non_strings = amp[fi].dropna()[~amp[fi].dropna().apply(type).eq(unicode)]
    if len(non_strings):
        logbuffer += u"\nCampo {0} tiene tipo inapropiado ({1} en vez de unicode).\n".format(
                        fi, non_strings.dtype)

if interactive:
    print logbuffer 
    logbuffer = u""


# In[ ]:


if len(amp[amp[CONS].duplicated()]):

    logbuffer += u"\nTabla {0} contiene indices duplicados.\n".format(ampie)

vym = pd.concat( [veg[CONS],amp[CONS]]) # Indices de vivos y muertos en pie

if len(vym[vym.duplicated()]):
    
    logbuffer += u"\nExisten indices duplicados en las tablas {0} y {1}.\n".format(veg, ampie)

for spf in amp[SPF].unique():
    
    if spf not in range(1,6):
        
        logbuffer += u"\nValor no valido de parcela: {0}\n".format(spf)
        
        logbuffer += amp[[SPF, PLOT]][amp[SPF] == spf].merge(info[[PLOT, SOCIO]], 
                        on=PLOT, how='left').to_string(index=False) + u"\n"
        
        amp.drop(amp[amp[SPF] == spf].index, inplace=True)

for tam in amp[TAMANO].unique():
    
    if tam not in [u'L', u'F', u'FG']:
        
        logbuffer += u"\nValor no valido de tamaño de individuo: {0}\n".format(tam)
        
if amp[AZIMUT].min() < 0:

    logbuffer += u"\nAzimut contiene valores no aceptados.\n"

if amp[AZIMUT].max() > 360:

    logbuffer += u"\nAzimut contiene valores no aceptados.\n"
    
# Verificar asignacion de clases diametricas
if len(amp[(amp[TAMANO] != u'B') & ((amp[DAPA] < 2.5) | ((amp[DAP1] + amp[DAP2]) < 5.0))]):

    logbuffer += u"\nBrinzales están asignados a categoria erronea:\n"

    logbuffer += amp[[PLOT, SPF, TAMANO, DAPA, DAP1, DAP2]][(amp[TAMANO] != u'B') & 
                    ((amp[DAPA] < 2.5) | ((amp[DAP1] + amp[DAP2]) < 5.0))].join(info[[u'PLOT', 
                    u'SOCIO']].set_index(PLOT), on=PLOT, rsuffix=u'_info').to_string(index=
                    False) + u"\n"
    
    amp.loc[(amp[TAMANO] != u'B') & ((amp[DAPA] < 2.5) | ((amp[DAP1] + amp[DAP2]) < 5.0)), TAMANO]         = u'B'

if len(amp[(amp[TAMANO] != u'L') & (((amp[DAPA] < 10) & (amp[DAPA] >= 2.5)) | (((amp[DAP1] + 
        amp[DAP2]) < 20) & ((amp[DAP1] + amp[DAP2]) >= 5.0)))]):
    
    logbuffer += u"\nLatizales están asignados a categoria erronea:\n"

    logbuffer += amp[[PLOT, SPF, TAMANO, DAPA, DAP1, DAP2]][(amp[TAMANO] != 'L') & 
                    (((amp[DAPA] < 10) & (amp[DAPA] >= 2.5)) | (((amp[DAP1] + amp[DAP2]) < 20) 
                    & ((amp[DAP1] + amp[DAP2]) >= 5.0)))].join(info[[u'PLOT', u'SOCIO']].set_index(
                    PLOT), on=PLOT, rsuffix=u'_info').to_string(index=False) + u"\n"

    amp.loc[(amp[TAMANO] != 'L') & (((amp[DAPA] < 10) & (amp[DAPA] >= 2.5)) | (((amp[DAP1] + 
        amp[DAP2]) < 20) & ((amp[DAP1] + amp[DAP2]) >= 5.0))), TAMANO] = u'L'
    
if len(amp[(amp[TAMANO] != u'F') & (((amp[DAPA] < 30) & (amp[DAPA] >= 10)) | (((amp[DAP1] + 
        amp[DAP2]) < 60) & ((amp[DAP1] + amp[DAP2]) >= 20)))]):
    
    logbuffer += u"\nFustales están asignados a categoria erronea:\n"
    
    logbuffer += amp[[PLOT, SPF, TAMANO, DAPA, DAP1, DAP2]][(amp[TAMANO] != 'F') & (((amp[DAPA] 
                    < 30) & (amp[DAPA] >= 10)) | (((amp[DAP1] + amp[DAP2]) < 60) & ((amp[DAP1] + 
                    amp[DAP2]) >= 20)))].join(info[[u'PLOT', u'SOCIO']].set_index(PLOT), on=PLOT, 
                    rsuffix=u'_info').to_string(index=False) + u"\n"
    
    amp.loc[(amp[TAMANO] != u'F') & (((amp[DAPA] < 30) & (amp[DAPA] >= 10)) | (((amp[DAP1] + 
            amp[DAP2]) < 60) & ((amp[DAP1] + amp[DAP2]) >= 20))), TAMANO] = u'F'
    
if len(amp[(amp[TAMANO] != u'FG') & ((amp[DAPA] >= 30) | ((amp[DAP1] + amp[DAP2]) >= 60))]):
    
    logbuffer += u"\nFustales grandes están asignados a categoria erronea:\n"
    
    logbuffer += amp[[PLOT, SPF, TAMANO, DAPA, DAP1, DAP2]][(amp[TAMANO] != 'FG') & ((amp[DAPA]
                    >= 30) | ((amp[DAP1] + amp[DAP2]) >= 60))].join(info[['PLOT', 'SOCIO']
                    ].set_index(PLOT), on=PLOT, rsuffix='_info').to_string(index=False) + u"\n"
    
    amp.loc[(amp[TAMANO] != u'FG') & ((amp[DAPA] >= 30) | ((amp[DAP1] + amp[DAP2]) >= 60)),
        TAMANO] = u'FG'

# Verificar si las distancias corresponden a las categorias de edad. Registros afuera 
# de sus respectivas areas son eliminados
if len(amp[(amp[DIST] > 3) & (amp[TAMANO] == u'L')]):
    
    logbuffer += u"\nLatizales registrados afuera del area aceptada:\n"
    
    logbuffer += amp[[TAMANO, DIST, DAPA, PLOT, SPF]][(amp[DIST] > 3) & (amp[TAMANO] == u'L')
                    ].join(info[[u'PLOT', u'SOCIO']].set_index(PLOT), on=PLOT, rsuffix=u'_info'
                    ).to_string(index=False) + u"\n"
    
    amp.drop(amp[(amp[DIST] > 3) & (amp[TAMANO] == u'L')].index, inplace=True)
    
if len(amp[(amp[DIST] > 7) & (amp[TAMANO] == u'F')]):
    
    logbuffer += u"\nFustales registrados afuera del area aceptada:\n"
    
    logbuffer += amp[[TAMANO, DIST, DAPA, PLOT, SPF]][(amp[DIST] > 7) & (amp[TAMANO] == u'F')
                    ].join(info[[u'PLOT', u'SOCIO']].set_index(PLOT), on=PLOT, rsuffix=u'_info'
                    ).to_string(index=False) + u"\n"
    
    amp.drop(amp[(amp[DIST] > 7) & (amp[TAMANO] == u'F')].index, inplace=True)
    
if len(amp[amp[DIST] > 15]):
    
    logbuffer += u"\nIndividuos registrados afuera del area de la subparcela:\n"
    
    logbuffer += amp[[TAMANO, DIST, DAPA, PLOT, SPF]][amp[DIST] > 15].join(info[[u'PLOT', 
                    u'SOCIO']].set_index(PLOT), on=PLOT, rsuffix=u'_info').to_string(index=
                    False) + u"\n"

    amp.drop(amp[amp[DIST] > 15].index, inplace = True)
    
# Altura total siempre debe ser mayor o igual a la altura del fuste
# Si la altura de fuste es mayor entonces es reemplazada con la altura total
if amp[amp[ALTF] > amp[ALTT]].size:
    
    logbuffer += u"\nIndividuos con altura del fuste mayor a la altura total:\n"
    
    logbuffer += amp[[ALTF, ALTT, PLOT, SPF]][amp[ALTF] > amp[ALTT]].join(info[[u'PLOT', 
                    u'SOCIO']].set_index(PLOT), on=PLOT, rsuffix=u'_info').to_string(index=
                    False) + u"\n"
    
    amp.loc[amp[ALTF] > amp[ALTT] , ALTF] = amp[amp[ALTF] > amp[ALTT]][ALTT]
    
# Punto de observacion de diametro
if len(amp[(amp[POM] > amp[ALTT]) | (amp[POM] > 10.0)]):
    
    logbuffer += u"\nValores de Punto de observacion de la medida mayores a la altura o "                     + u"mayores a 10 m.\n"
    
    logbuffer += amp[[ALTT, ALTF, POM, FORMA_FUSTE, PLOT, SPF]][(amp[POM] > amp[ALTT]) | 
                    (amp[POM] > 10.0)].merge(info[[PLOT, SOCIO]], on=PLOT, how='left'
                    ).to_string(index=False) + u"\n"

    # Se asume que todos los valores mayores a 10 m o a la altura total fueron erroneamente
    # multiplicados por 10. Queda pendiente decidir que hacer con los valores mayores a 2 m
    # de tallo cilindrico
    amp.loc[((amp[POM] > amp[ALTT]) | (amp[POM] > 10.0)), POM] = amp[POM][(amp[POM] > 
        amp[ALTT])] / 10.0
    
# Informacion Penetrometro
if amp[PI_cm].min() < 0:
    
    logbuffer += u"\nHay valores negativos de entrada del penetrometro.\n"
    
if amp[PI_cm].max() > 20:
    
    logbuffer += u"\nValores maximos del entrada del penetrometro mayores al valor sugerido"                     +  u"en el manual:\n"

    logbuffer += amp[[PI_cm, PLOT, SPF]][amp[PI_cm] > 20].join(info[['PLOT', 'SOCIO']].set_index(
            PLOT), on=PLOT, rsuffix='_info').to_string(index=False) + u"\n"
    
    # Valores mayores a 20 cm son reestablecidos a 20 cm
    amp.loc[amp[PI_cm] > 20 , PI_cm] = 20

if len(amp[PI_cm][(amp[PI_cm] > amp[DAP1]) | (amp[PI_cm] > amp[DAP2])]):
    
    logbuffer += u"\nValores de entrada del penetrómetro son mayores al diametro registrado:\n"
    
    logbuffer += amp[[PI_cm, DAP1, DAP2, PLOT, SPF]][(amp[PI_cm] > amp[DAP1]) | (amp[PI_cm] 
                    > amp[DAP2])].join(info[[u'PLOT', u'SOCIO']].set_index(PLOT), on=PLOT, 
                    rsuffix=u'_info').to_string(index=False) + u"\n"
    
    # Se asume que la medida del penetrometro equivale al diametro
    amp.loc[(amp[PI_cm] > amp[DAP1]), PI_cm] = amp[DAP1][(amp[PI_cm] > amp[DAP1])]

if amp[PI_golpes].min() < 0:
    
    logbuffer += u"\nValores negativos de golpes al penetrometro.\n"
    
if amp[PI_golpes].max() > 25:
    
    logbuffer += u"\nValores maximos de golpes del penetrometro son dudosos:\n"
    
    logbuffer += amp[[PI_golpes, PLOT, SPF]][amp[PI_golpes] > 20].join(info[[u'PLOT', u'SOCIO']
                    ].set_index(PLOT), on=PLOT, rsuffix=u'_info').to_string(index=False) + u"\n"

# Depurar valores de forma de fuste a las abbreviaturas aceptadas
amp[FORMA_FUSTE].replace(to_replace=[r'\s+', u''], value=[u'', np.nan], regex=True, 
    inplace = True)

amp[FORMA_FUSTE] = amp[FORMA_FUSTE].str.upper()

# Los sigueintes son cambios basados en la presupocion de errores en el momento de ingresar datos
# en el formato de toma de datos. 

amp.loc[((amp[FORMA_FUSTE] == u'HI') | (amp[FORMA_FUSTE] == u'Q')) , FORMA_FUSTE] = np.nan
amp.loc[((amp[DANO] == u'IRR') & amp[FORMA_FUSTE].isna()) , FORMA_FUSTE] = u'IRR'
amp.loc[((amp[DANO] == u'IRR') & (amp[FORMA_FUSTE] == u'IRR')) , DANO] = np.nan


if interactive:
    print logbuffer 
else:
    with cd.open(logfile, mode='a', encoding='utf-8') as fhandle:
        fhandle.write(logbuffer)
logbuffer = u""


# # Coordenadas

# In[ ]:


CONS = u'CONS' # Indice coordenada (int64)
PLOT = u'PLOT' # Indice conglomerado (int64)
SPF = u'SPF' # Indice subparcela dentro del conglomerado (int64 1-5)
SUBPLOT = u'SUBPLOT' # Concatenacion PLOT "_" SPF (str)
LATITUD = u'LATITUD' # Latitud en formato decimal (float64)
LONGITUD = u'LONGITUD' # Longitud en formato decimal (float64)
REGION = u'REGION' # Region biogeografica (str: 'Amazonia', 'Andes', 'Pacifico', 'Orinoquia',
                  # 'Caribe')
ZV = u'ZV' # Zona de vida???????? (int64, 3, 4, 5, 6, 7, 13, 14, 15, 19, 20, 21, 27)
ZONA_VIDA = u'ZONA_VIDA' # Zona de vida (str: "Bosque húmedo tropical",  
    # "Bosque muy húmedo tropical",  "Bosque húmedo montano bajo",  "Bosque pluvial premontano",  
    # "Bosque muy húmedo premontano",  "Bosque húmedo premontano",  "Bosque muy húmedo montano",  
    # "Bosque seco tropical",  "Bosque muy húmedo montano bajo",  "Bosque seco montano bajo",  
    # "Bosque muy seco tropical",  "Monte espinoso subtropical")
EQ = u'EQ' # Ecuacion alometrica???? (int64: 1, 2, 4, 5, 6)
E_CHAVE = u'E_CHAVE' # Coeficiente de la ecuacion de Chave (float64)


# In[ ]:


logbuffer = u"\n" + u"#" * 50 + u"\nTABLA COORDENADAS\n"

for fi in [CONS, PLOT, SPF, ZV, EQ]:
    
    if coord[fi].dtype != np.int64:
        
        logbuffer += u"\nCampo {0} tiene tipo inapropiado ({1} en vez de int64).\n".format(
                        fi, coord[fi].dtype)
        
        if len(coord[fi][coord[fi].isna()]) > 1:
            
            logbuffer += u"\nLos siguentes valores nulos son considerados np.float64 por Pandas:\n"
            
            logbuffer += coord[[fi, PLOT, SPF]][amp[fi].isna()].merge(info[[PLOT, SOCIO]], 
                            on=PLOT, how='left').to_string(index=False) + u"\n"
            
        else:
            
            logbuffer += u"\nValores np.float64 a revisar:\n"
            
            logbuffer += coord[[fi, PLOT, SPF]][coord[fi].map(lambda x: x % 1.0 != 0)].dropna(
                            ).merge(info[[PLOT, SOCIO]], on=PLOT, how='left').to_string(index=
                            False) + u"\n"
            
            
for fi in [LATITUD, LONGITUD, E_CHAVE]:
    
    if coord[fi].dtype != np.float64:
        
        logbuffer += u"\nCampo {0} tiene tipo inapropiado ({1} en vez de float64)\n.".format(
                        fi, coord[fi].dtype)
        
        
for fi in [REGION, ZONA_VIDA]:
    
    non_strings = coord[fi].dropna()[~coord[fi].dropna().apply(type).eq(unicode)]
    
    if len(non_strings):
        
        logbuffer += u"\nCampo {0} tiene tipo inapropiado ({1} en vez de unicode).\n".format(
                        fi, non_strings.dtype)

if interactive:
    print logbuffer
    logbuffer = u""


# In[ ]:


# Verificar que los indices no están duplicados
if len(coord[coord[CONS].duplicated()]):
    logbuffer += u"\nTabla {0} contiene indices duplicados\n.".format(coordenadas)

# Verificar rangos de coordenadas 
lat_range = (-5, 15)
lon_range = (-80, -65)

if coord[LATITUD].min() < lat_range[0] or coord[LATITUD].max() > lat_range[1]:
    
    logbuffer +=  "\nLatitud fuerra de rango aceptado.\n"
    
if coord[LONGITUD].min() < lon_range[0] or coord[LONGITUD].max() > lon_range[1]:
    
    logbuffer +=  "\nLongitud fuerra de rango aceptado\n"

# Verificar region geografica    
for re in coord[REGION].unique():
    
    if re not in [u'Amazonia', u'Andes', u'Pacifico', u'Orinoquia', u'Caribe']:
        
        logbuffer += u"\nRegion biogeografica no aceptada: {0}\n".format(re)

# Verificar que todas las parcelas están georeferenciadas
integ = info[[PLOT,SPFC]].merge(coord[[PLOT, SPF, LATITUD, LONGITUD]], on=[PLOT], 
            how='left')

if len(integ[integ[LATITUD].isna() | integ[LONGITUD].isna()]):
    
    logbuffer +=  "\nAlgunas parcelas no tienen coordenadas geograficas:\n"
    
    logbuffer += integ[integ[LATITUD].isna() | integ[LONGITUD].isna()].to_string(index=
                    False) + u"\n"
    
if interactive:
    print logbuffer 
else:
    with open(logfile, 'a') as fhandle:
        fhandle.write(logbuffer)
logbuffer = u""


# # Inclusion de información en la base de datos
# Se incluyen los datos depurados en la base de datos MySQL a través del módulo SQLAlchemy. El esquema de la base de datos debe ser incluido con anterioridad al servidor local. Una copia del esquema está disponible en el archivo `Esquema_Inventario.sql`.

# In[ ]:


import sqlalchemy as al

engine = al.create_engine(
    'mysql+mysqldb://{0}:{1}@localhost/IFN?charset=utf8&use_unicode=1'.format(user, password),
    encoding='utf-8')

con = engine.connect()
# Desactivar la verificación de foreign keys para la inserción en lote
con.execute('SET foreign_key_checks = 0')


# In[ ]:


# Tabla Analizador

analiz.rename(columns = {CONS: u"AnalisisID", PLOT: u"Plot", SPF: u"Subparcela", N: u"Nitrogeno",
    C: u"Carbono"}).to_sql("Analizador", con, if_exists = "append", index = False)


# In[ ]:


# Tabla Carbono

carb.rename(columns = {CONS: u"CarbonoID", PLOT: u"Plot", SPF: u"Subparcela", C: u"Contenido",
    SUELO: u"Masa", RAIZ: u"Raiz", ROCA: u"Roca", VOL: u"Volumen", DENS: u"Densidad"}).to_sql(
    "Carbono", con, if_exists = "append", index = False)


# In[ ]:


# Tabla Fertilidad

fert.rename(columns = {CONS: u"FertID", PLOT: u"Plot", TEXTURA: u"Textura", MO: u"MateriaOrganica",
    A: u"Arena", L: u"Limo", Ar: u"Arcilla", pH: u"pH", CICE: u"CICE", Al: u"Aluminio", Ca: u"Calcio",
    Cu: u"Cobre", P: u"Fosforo", Fe: u"Hierro", Mg: u"Magnesio", Mn: u"Manganeso", N: u"Nitrogeno",
    K: u"Potasio", Zn: u"Zinc"}).to_sql("Fertilidad", con, if_exists = "append", index = False)


# In[ ]:


# Tabla Coordenadas

coord[[PLOT, SPF, LATITUD, LONGITUD, ZV, ZONA_VIDA, EQ, E_CHAVE]].rename(columns = {PLOT: u'Plot', 
    SPF: u'SPF', LATITUD: u'Latitud', LONGITUD: u'Longitud', ZV: u'ZV', ZONA_VIDA: u'ZonaVida', 
    EQ: u'Eq', E_CHAVE: u'ChaveE'}).to_sql('Coordenadas', con, if_exists = 'append', index = False)


# In[ ]:


# Tabla Conglomerados

info[[PLOT, DEPARTAMENTO, REGION, FECHA_CAMPO, SOCIO, SPFC]].rename(columns = {PLOT: u'PlotID',
    DEPARTAMENTO: u'Departamento', REGION: u'Region', FECHA_CAMPO: u'Fecha', SOCIO: u'Socio', 
    SPFC: u'SFPC'}).to_sql('Conglomerados', con, if_exists = 'append', index = False)


# In[ ]:


# Tabla Taxonomia

tax = {}

for row in veg[[FAMILIA, GENERO, EPITETO, AUTOR]].itertuples():
    tax[(row[1], row[2], row[3])] = row[4]
    
taxtemp = {FAMILIA:[], GENERO:[], EPITETO:[], AUTOR:[]}

for (fam, gen, epi) in tax:
    taxtemp[FAMILIA].append(fam)
    taxtemp[GENERO].append(gen)
    taxtemp[EPITETO].append(epi)
    taxtemp[AUTOR].append(tax[(fam, gen, epi)])

tax = None
taxdf = pd.DataFrame.from_dict(taxtemp)
taxtemp = None

if taxdf.index[0] == 0:
    taxdf.index += 1
    
taxdf[u'Fuente'] = 1

taxdf.rename(columns = {FAMILIA: u'Familia', GENERO: u'Genero', AUTOR: u'Autor', EPITETO: u'Epiteto'}
    ).to_sql('Taxonomia', con, if_exists='append', index_label=u'TaxonID')


# In[ ]:


# Tabla Determinaciones

if u'Taxon' not in taxdf.columns:
    taxdf[u'Taxon'] = taxdf.index

if 'Taxon' not in veg:
    veg = veg.merge(taxdf[[FAMILIA, GENERO, EPITETO, u'Taxon']], on=[FAMILIA, GENERO, EPITETO],
            how='left', suffixes = [u'_l', u'_r'])

deters = veg.groupby(by=[PLOT, IND, u'Taxon']).size().reset_index().drop(axis=1, labels=0)

if deters.index[0] == 0:
    deters.index += 1

deters[u'DetID'] = deters.index
deters[[u'Taxon', u'DetID']].to_sql('Determinaciones', con, if_exists='append', index=False)


# In[ ]:


# Tabla individuos

if u'DetID' not in veg.columns:
    veg = veg.merge(deters[[PLOT, IND, u'DetID']], on=[PLOT, IND], how='left')

indAll = pd.concat([veg[[PLOT, IND]], amp[[PLOT, IND]]]).sort_values([PLOT,IND]).reset_index(
    ).drop(axis=1, labels='index')
indAll = indAll[~indAll.duplicated()]
if indAll.index[0] == 0:
    indAll.index += 1
indAll['IndividuoID'] = indAll.index

# Remover individuos con tallos multiples vivos Y muertos de la tabla arboles muerto en pie (amp)
zombies = veg.merge(amp, on=[PLOT,IND], how = 'inner')[[PLOT, IND]]
iz = zombies.set_index([PLOT,IND]).index
ia = amp.set_index([PLOT,IND]).index
amp_no_dups = amp.drop(amp[ia.isin(iz)].index)

indpart = pd.concat([veg[[SPF, AZIMUT, DIST, PLOT, IND, u'DetID']], amp_no_dups[[SPF, AZIMUT, DIST, 
                PLOT, IND]]])

indAll = indAll.merge(indpart, on=[PLOT, IND], how='inner').drop_duplicates(subset=u'IndividuoID')

indAll[[PLOT, AZIMUT, SPF, DIST, u'DetID']].rename(columns = {PLOT: u'Plot', SPF: u'Subparcela', 
    AZIMUT: u'Azimut', DIST: u'Distancia', u'DetID': u'Dets'}).to_sql('Individuos', con, 
    if_exists = 'append', index = False)


# In[ ]:


# Tabla Tallos

tallosparc = pd.concat([veg, amp])
tallos = tallosparc.merge(indAll, on=[PLOT, IND], how='inner')
tallos[[CONS, DAP1, DAP2, DAPA, DAP_EQUIPO, TAMANO, FORMA_FUSTE, ALTF, ALTT, ALT_EQUIPO, 
    u'IndividuoID', COND, POM, DANO, PI_cm, PI_golpes]].rename(columns = {CONS: u'TalloID', 
    DAP1: u'Diametro1', DAP2: u'Diametro2', DAPA: u'DiametroP', DAP_EQUIPO: u'EquipoDiam', 
    TAMANO: u'Tamano', FORMA_FUSTE: u'FormaFuste', ALTF: u'AlturaFuste', ALTT: u'AlturaTotal', 
    ALT_EQUIPO: u'EquipoAlt', u'IndividuoID': u'Individuo', COND: u'Condicion', POM: u'POM', 
    DANO: u'Dano', PI_cm: u'PetrProf', PI_golpes: u'PetrGolpes'}).to_sql(u'Tallos', con, 
    if_exists = 'append', index = False)


# In[ ]:


# Tabla Detritos
PI_cm, PI_golpes = u'PI_cm', u'PI_golpes'

det[[CONS, PLOT, TRAN, SECC, PIEZA, TIPO, DIST, AZIMUT, D1, D2, INCL, PI_cm, PI_golpes, 
    PESO_RODAJA, PESO_MUESTRA, PESO_SECO, ESP1, ESP2, ESP3, ESP4, VOL, DENS]].rename(
    columns = {CONS: u'DETRITOID', PLOT: u'PLOT', TRAN: u'Transecto', SECC: u'Seccion', 
    PIEZA: u'Pieza', TIPO: u'Tipo', DIST: u'Distancia', AZIMUT: u'Azimut', D1: u'Diametro1', 
    D2: u'Diametro2', INCL: u'Inclinacion', PI_cm: u'PetrProf', PI_golpes: u'PetrGolpes',
    PESO_RODAJA: u'PesoRodaja', PESO_MUESTRA: u'PesoMuestra', PESO_SECO: u'PesoSeco', 
    ESP1: u'Espesor1', ESP2: u'Espesor2', ESP3: u'Espesor3', ESP4: u'Espesor4', 
    VOL: u'Volumen', DENS: u'Densidad'}).to_sql(u'Detritos', con, 
    if_exists = 'append', index = False)


# In[ ]:


# Restituir la verificación de foreign keys
con.execute('SET foreign_key_checks = 1')
con.close()

