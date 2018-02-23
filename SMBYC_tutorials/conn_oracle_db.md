# Conexión a la base de datos maestra en Oracle

Este tutorial enseña los pasos requeridos para acceder a la base maestra del IFN a través de Python, usando las librerías sqlalchemy y pandas. Se asume que el sistema operativo de trabajo es Linux y que sqlalchemy y pandas ya han sido previamente instalados.


## Instalación de software

1. Descargue el cliente básico de Oracle en la [pagina de descarga](http://www.oracle.com/technetwork/topics/linuxx86-64soft-092277.html), versión RPM. 

2. Instale Alien: `sudo apt-get install alien`.

3. Instale el cliente: `sudo alien -i <nombre_del_archivo_rpm`.

4. Instale libaio: `sudo apt-get install libaio-dev`. 

5. Instalar la librery cx_Oracle. Si se utiliza conda: `sudo conda install cx\_oracle`. Si se utiliza pip: `sudo pip cx\_oracle`.


## Configuración

Las librerías del cliente están usuanmente instaladas en la carpeta `/usr/lib/oracle/<#>/client64/lib`.
Un par de variables del sistema deben apuntar a dicha locación, y una copia debe establecerse.

1. Generar un link simbólico a una de las librerías recién instaladas:  

```
cd /usr/lib/oracle/12.2/client64/lib
ln -s libclntsh.so.12.1 libclntsh.so
```

2. Creación de las variables del sistema:

```
export ORACLE\_HOME=/usr/lib/oracle/12.2/client64/lib
export LD\LIBRARY\PATH=$ORACLE_HOME:$LD_LIBRARY_PATH
```

3. Configuración del dynamic linker: `sudo ldconfig`

Los datos del punto dos pueden guardarse en el perfil del usuario (`.bashrc`) para realizarlo una sola vez.


## Connección en Python

1. Generación del SID extendido:
```python
import cx_Oracle
ext_sid = cx_Oracle.makedsn(<host>, <port>, <sid>)
eng = al.create_engine("oracle+cx_oracle://username:password@{0}".format(ext_sid))
conn = conntect()
dtfr = pd.read_sql_table(con=conn, table_name=<nombre_de_la_tabla>) 
```

