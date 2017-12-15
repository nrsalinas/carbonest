
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

# Si el script es ejecutado interactivamente (como un cuaderno Jupyter, por ejemplo)
# la variable `interactive` debe ser `True`, de lo contrario los reportes de error
# serán guardados en un archivo de texto (`logfile`).
interactive = True 

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

# Leer archivos como Pandas dataframes
det = pd.read_csv(detritos, encoding = 'utf8') 
amp = pd.read_csv(ampie, encoding = 'utf8')
veg = pd.read_csv(vegetacion, encoding = 'utf8')
info = pd.read_csv(generalInfo, encoding = 'utf8')
coord = pd.read_csv(coordenadas, encoding = 'utf8')


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
        logbuffer += u"\nCampo {0} tiene tipo inapropiado ({1} en vez de int64).\n".format(fi, det[fi].dtype)
        if len(det[fi][det[fi].isna()]) > 1:
            logbuffer += u"\nValores nulos son considerados np.float64:\n"
            logbuffer += det[[CONS, fi, PLOT, TRAN]][det[fi].isna()].join(info[[u'PLOT', u'SOCIO']
                            ].set_index(PLOT), on=PLOT, rsuffix=u'_info').to_string(index=False) + "\n"
        else:
            logbuffer += u"\nValores np.float64 a revisar:\n"
            logbuffer += det[fi][det[fi].map(lambda x: x % 1.0 != 0)].dropna().to_string() + "\n"
        
for fi in [AZIMUT, PIEZA, DIST, D1, D2, INCL, PI_cm, PESO_RODAJA, ESP1, ESP2, ESP3, ESP4, 
           PESO_MUESTRA, VOL, PESO_SECO, DENS, PI_golpes]:
    if det[fi].dtype != np.float64:
        logbuffer += u"\nCampo {0} tiene tipo inapropiado ({1}en vez de float64).\n".format(fi, det[fi].dtype)

for fi in [TRAN, TIPO]:
    non_unicode = det[fi].dropna()[~det[fi].dropna().apply(type).eq(unicode)]
    if len(non_unicode):
        logbuffer += u"\nCampo {0} tiene tipo inapropiado ({1} en vez de unicode).\n".format(fi, non_strings.dtype)

if interactive:
    print logbuffer    
    logbuffer = u""


# In[ ]:

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
        
if len(det[(det[TIPO] == u'DFM') & (((det[D1] >= 20) & (det[D2].isna())) | (det[D1] + det[D2] >= 40))]):
    logbuffer += u"\nTipo de detrito probablemente mal asignado\n"
    logbuffer += det[[CONS, TIPO, D1, D2, PLOT, TRAN]][(det[TIPO] == u'DFM') & (((det[D1] >= 20) 
                    & (det[D2].isna())) | (det[D1] + det[D2] >= 40))].join(info[[u'PLOT', 
                    u'SOCIO']].set_index(PLOT), on=PLOT, rsuffix=u'_info').to_string(index = 
                    False) + "\n"
    det.loc[(det[TIPO] == u'DFM') & (((det[D1] >= 20) & (det[D2].isna())) | (det[D1] + det[D2] >= 40)
        ), TIPO] = u'DGM'

if len(det[(det[TIPO] == u'DGM') & (((det[D1] < 20) & (det[D2].isna())) | (det[D1] + det[D2] < 40))]):
    logbuffer += u"\nTipo de detrito probablemente mal asignado\n"
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
    
    
##############################################
# Al parecer las medidas de distancia de DFM menores a 9 realmente fueron realizadas con el 
# punto de referencia adecuado. Teoricamente la zona de la seccion a ser considerada para
# DFM fue modificada a lo largo de la ejecucion del proyecto.
#
# Correcciones de distancias mayores a 10 
# Al parecer las medidas mayores a 10 m y menores a 30 m 
# fueron realizadas sin reestablecer el punto de 
# referencia al inicio de las secciones 2 y 3.
##############################################

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

if det[AZIMUT].min() < 0:
    logbuffer += u"\nRango Azimut tiene valores negativos.\n"
if det[AZIMUT].max() > 360:
    logbuffer += u"\nRango Azimut sobrepasa el valor permitido (360)\n"

#####################################################
# Valores dudosos de diametro
# Valores de diametro 0.0 deben ser nulos
det[D2].replace(to_replace = 0.0, value = np.nan, inplace = True)

# Detritos con diametro menor a 2 cm son eliminados
if len(det[(det[D1] + det[D2]) < 4]):
    logbuffer += u"\nRango de diametro tiene valores inferiores a 2 cm.\n"
    logbuffer += det[[CONS, D1, D2, PLOT, TRAN]][(det[D1] + det[D2]) < 4].join(info[[
                    u'PLOT', u'SOCIO']].set_index(PLOT), on=PLOT, rsuffix=u'_info').to_string(
                    index=False) + "\n"
    det.drop(det[(det[D1] + det[D2]) < 4].index, inplace=True)
    
#
# ¿Como tratar los valores de inclinación? ¿Están simplemente desfazados 90 grados?
#   
if det[INCL].min() < -90:
    logbuffer += u"\nRango inclinacion tiene valores menores al valor permitido (-90).\n"
    logbuffer += det[[CONS, INCL, PLOT, TRAN]][det[INCL] < -90].join(info[[u'PLOT', u'SOCIO']
                    ].set_index(PLOT), on=PLOT, rsuffix=u'_info').to_string(index=False) + "\n"
if det[INCL].max() > 90:
    logbuffer += u"\nRango inclinacion sobrepasa el valor permitido (90)\n"
    logbuffer += det[[CONS, INCL, PLOT, TRAN]][det[INCL] > 90].join(info[[u'PLOT', u'SOCIO']
                    ].set_index(PLOT), on=PLOT, rsuffix=u'_info').to_string(index=False) + "\n"
    
if det[PI_cm].min() < 0:
    logbuffer += u"\nHay valores negativos de entrada del penetrometro.\n"
if det[PI_cm].max() > 20:
    logbuffer += u"\nValores maximos del entrada del penetrometro mayores al valor sugerido en el manual:\n"
    #print det[[PI_cm, D1, D2]][det[PI_cm] > 20]
    logbuffer += det[[CONS, PI_cm, PLOT, TRAN]][det[PI_cm] > 20].join(info[[u'PLOT', u'SOCIO']
                    ].set_index(PLOT), on=PLOT, rsuffix=u'_info').to_string(index=False) + "\n"
    # Valores mayores a 20 cm son ajustados a 20 cm
    det.loc[det[PI_cm] > 20 , PI_cm] = 20

if len(det[PI_cm][(det[PI_cm] > det[D1]) | (det[PI_cm] > det[D2])]):
    logbuffer += u"\nValores de entrada del penetrometro son mayores al diametro registrado:\n"
    logbuffer += det[[CONS, PI_cm, D1, D2, PLOT, TRAN]][(det[PI_cm] > det[D1]) | (det[PI_cm] 
                    > det[D2])].join(info[[u'PLOT', u'SOCIO']].set_index(PLOT), on=PLOT, 
                    rsuffix=u'_info').to_string(index=False) + "\n"

if det[PI_golpes].min() < 0:
    logbuffer += u"\nValores negativos de golpes al penetrometro.\n"
if det[PI_golpes].max() > 25:
    logbuffer += u"\nValores maximos de golpes del penetrometro son dudosos:\n"
    logbuffer += det[[CONS, PI_golpes, PLOT, TRAN]][det[PI_golpes] > 20].join(info[[u'PLOT', 
                    u'SOCIO']].set_index(PLOT), on=PLOT, rsuffix=u'_info').to_string(index = 
                    False) + "\n"
    
# Sets de valores de espesor de pieza son dudosos si la desviacion estandar es mayor a 0.3 
# la media del set
if len(det[(det[[ESP1, ESP2, ESP3, ESP4]].std(1) / det[[ESP1, ESP2, ESP3, ESP4]].mean(1)) > 0.3]):
    logbuffer += u"\nAlgunos conjuntos de espesor de pieza tienen una variacion muy alta:\n"
    logbuffer += det[[CONS, ESP1, ESP2, ESP3, ESP4, PLOT, TRAN]][(det[[ESP1, ESP2, ESP3, ESP4]
                    ].std(1) / det[[ESP1, ESP2, ESP3, ESP4]].mean(1)) > 0.3].join(info[[u'PLOT', 
                    u'SOCIO']].set_index(PLOT), on=PLOT, rsuffix=u'_info').to_string(index =
                    False) + "\n"
    
if det[(det[PESO_MUESTRA] < det[PESO_SECO]) | (det[PESO_MUESTRA].isna() & (det[PESO_RODAJA] < 
        det[PESO_SECO]))].size:
    logbuffer += u"\nPeso fresco es menor al peso seco:\n"
    logbuffer += det[[CONS, PESO_MUESTRA, PESO_RODAJA, PESO_SECO, PLOT, TRAN]][(det[PESO_MUESTRA] 
                    < det[PESO_SECO]) | (det[PESO_MUESTRA].isna() & (det[PESO_RODAJA] < 
                    det[PESO_SECO]))].join(info[[u'PLOT', u'SOCIO']].set_index(PLOT), on=PLOT, 
                    rsuffix=u'_info').to_string(index = False) + "\n"

if det[(det[PESO_MUESTRA] > det[PESO_RODAJA])].size:
    logbuffer += u"\nPeso del fragmento muestreado es mayor al de la rodaja:\n"
    logbuffer += det[[CONS, TIPO, PESO_MUESTRA, PESO_RODAJA, PESO_SECO, PLOT, TRAN]][
                    (det[PESO_MUESTRA] > det[PESO_RODAJA])].join(info[[u'PLOT', u'SOCIO']
                    ].set_index(PLOT), on=PLOT, rsuffix=u'_info').to_string(index=False) + "\n"
    
if det[det[PESO_MUESTRA].isna() & det[PESO_RODAJA].isna()].size:
    logbuffer += u"\nFalta peso fresco de detrito:\n"
    logbuffer += det[[CONS, TIPO, PESO_MUESTRA, PESO_RODAJA, PESO_SECO, PLOT, TRAN]][
                    det[PESO_MUESTRA].isna() & det[PESO_RODAJA].isna()].join(info[[u'PLOT', 
                    u'SOCIO']].set_index(PLOT), on=PLOT, rsuffix=u'_info').to_string(index
                    = False) + "\n"
    
if interactive:
    print logbuffer 
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

# Verificar estimacion DAP promedio
if veg[((veg[DAP1] + veg[DAP2]) - (veg[DAPA] * 2)) > 0.1].size:
    
    logbuffer += u"\nErrores en la estimación del DAP promedio?:\n"
    
    logbuffer += veg[[CONS, DAPA, DAP1, DAP2, PLOT, SPF]][((veg[DAP1] + veg[DAP2]) - 
                    (veg[DAPA] * 2)) > 0.01].join(info[[u'PLOT', u'SOCIO']].set_index(PLOT),
                    on=PLOT, rsuffix=u'_info').to_string(index=False) + "\n"

# Altura total siempre debe ser mayor a la altura del fuste
if veg[veg[ALTF] > veg[ALTT]].size:
    
    logbuffer += u"\nIndividuos con altura del fuste mayor a la altura total:"
    
    logbuffer += veg[[CONS, ALTF, ALTT, PLOT, SPF]][veg[ALTF] > veg[ALTT]].join(info[[u'PLOT',
                    u'SOCIO']].set_index(PLOT), on = PLOT, rsuffix = u'_info').to_string(index
                    =False) + "\n"

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
SPFC = u'SPF-C' # ??????? (int64 0-5)
FERT = u'FERT' # Estimacion fertilidad ????????????? (str: 'Si', 'No'). Deberia ser boolean.
DETR = u'DETR' # Toma de detritos ????????? (str: 'Si', 'No'). Deberia ser boolean.


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

###########################################
# Se asume que los campos BOT_TOT, fertilidad y detritos son boolean en ves de texto
###########################################
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

if len(amp[(amp[TAMANO] != u'L') & (((amp[DAPA] < 10) & (amp[DAPA] >= 2.5)) | (((amp[DAP1] + 
        amp[DAP2]) < 20) & ((amp[DAP1] + amp[DAP2]) >= 5.0)))]):
    
    logbuffer += u"\nLatizales están asignados a categoria erronea:\n"

    logbuffer += amp[[PLOT, SPF, TAMANO, DAPA, DAP1, DAP2]][(amp[TAMANO] != 'L') & 
                    (((amp[DAPA] < 10) & (amp[DAPA] >= 2.5)) | (((amp[DAP1] + amp[DAP2]) < 20) 
                    & ((amp[DAP1] + amp[DAP2]) >= 5.0)))].join(info[[u'PLOT', u'SOCIO']].set_index(
                    PLOT), on=PLOT, rsuffix=u'_info').to_string(index=False) + u"\n"
    
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

# Verificar si las distancias corresponden a las categorias de edad.
if len(amp[(amp[DIST] > 3) & (amp[TAMANO] == u'L')]):
    
    logbuffer += u"\nLatizales registrados afuera del area aceptada:\n"
    
    logbuffer += amp[[TAMANO, DIST, DAPA, PLOT, SPF]][(amp[DIST] > 3) & (amp[TAMANO] == u'L')
                    ].join(info[[u'PLOT', u'SOCIO']].set_index(PLOT), on=PLOT, rsuffix=u'_info'
                    ).to_string(index=False) + u"\n"
    
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

# Altura total siempre debe ser mayor a la altura del fuste
if amp[amp[ALTF] > amp[ALTT]].size:
    
    logbuffer += u"\nIndividuos con altura del fuste mayor a la altura total:\n"
    
    logbuffer += amp[[ALTF, ALTT, PLOT, SPF]][amp[ALTF] > amp[ALTT]].join(info[[u'PLOT', 
                    u'SOCIO']].set_index(PLOT), on=PLOT, rsuffix=u'_info').to_string(index=
                    False) + u"\n"
    
# Punto de observacion de diametro
if len(amp[(amp[POM] > amp[ALTT]) | (amp[POM] > 10.0)]):
    
    logbuffer += u"\nValores de Punto de observacion de la medida mayores a la altura o"                     + u"mayores a 10 m.\n"
    
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

# Tabla Coordenadas

coord[[PLOT, SPF, LATITUD, LONGITUD, ZV, ZONA_VIDA, EQ, E_CHAVE]].rename(columns = {PLOT: u'Plot', SPF: u'SPF',
    LATITUD: u'Latitud', LONGITUD: u'Longitud', ZV: u'ZV', ZONA_VIDA: u'ZonaVida', EQ: u'Eq', E_CHAVE: u'ChaveE'}
    ).to_sql('Coordenadas', con, if_exists = 'append', index = False)


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
veg = veg.merge(deters[[PLOT, IND, u'DetID']], on=[PLOT, IND], how='left')

indtemp0 = veg.groupby(by=[PLOT, IND]).size().reset_index().drop(axis=1, labels=0)
indtemp1 = amp.groupby(by=[PLOT, IND]).size().reset_index().drop(axis=1, labels=0)

indtemp = pd.concat([indtemp0, indtemp1]).reset_index()

indtemp.index += 1
indtemp['IndividuoID'] = indtemp.index

indtemp2 = pd.concat([veg[[SPF, AZIMUT, DIST, PLOT, IND, u'DetID']], amp[[SPF, AZIMUT, DIST, 
                PLOT, IND]]])

indiv = indtemp.merge(indtemp2, on=[PLOT, IND], how='left').drop_duplicates(subset=u'IndividuoID')

indiv[[PLOT, AZIMUT, SPF, DIST, u'DetID']].rename(columns = {PLOT: u'Plot', SPF: u'Subparcela', 
    AZIMUT: u'Azimut', DIST: u'Distancia', u'DetID': u'Dets'}).to_sql('Individuos', con, 
    if_exists = 'append', index = False)


# In[ ]:

# Tabla Tallos
###############################
# Hay arboles muertos y vivos con misma combinacion 
# (conglomerado, numero de individuo en conglomerado)
###############################

tallosparc = pd.concat([veg, amp])
tallos = tallosparc.merge(indiv, on=[PLOT, IND], how='inner')
tallos.drop_duplicates(subset=CONS, inplace=True)
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

