"""
Final taxonomic updates for databases. Assumes database `Quimera` was loaded from
backup file `Quimera_20180110.sql` and database `IFN` from `IFN_20180112.sql`.

DB backups after execution of this script were saved in `Quimera_20180113.sql`
and `IFN_20180113.sql`.
"""
import sqlalchemy as al
import pandas as pd

user = ""
password = ""
database = ""


# Archivo csv con la clasificacion actualizada de las plantas con semilla.
# Contiene dos columnas: genero (`Genus`) y familia (`Family`)
tpl_file = '/home/nelson/Documents/IDEAM/carbonest/seed_plants_genera_20180113.csv'

engine = al.create_engine(
	'mysql+mysqldb://{0}:{1}@localhost/{2}?charset=utf8&use_unicode=1&unix_socket=/var/run/mysqld/mysqld.sock'.format(
	user, password, database), encoding='utf-8')

conn = engine.connect()
tax = pd.read_sql_table(table_name='Taxonomia',con=conn) #, index_col='TaxonID')


# Eliminar generos indet duplicados
for ge in tax.Genero.unique():
	if len(tax[(tax.Genero == ge) & tax.Epiteto.isna()]) > 1:
		chosenDad = tax[(tax.Genero == ge) & tax.Epiteto.isna()]['TaxonID'].tolist()[0]
		for dad in tax[(tax.Genero == ge) & tax.Epiteto.isna()]['TaxonID']:
			tax.loc[(tax.SinonimoDe == dad), 'SinonimoDe'] = chosenDad
			if int(dad) != int(chosenDad):
				tax.drop(index = tax[tax.TaxonID == dad].index , inplace = True)


# Homogenizar familias
tax.Familia = tax.Familia.str.title()

# eliminar autoreferencias de sinonimia
tax.loc[(tax.SinonimoDe == tax.TaxonID), 'SinonimoDe'] = None


# Corregir clasificacion de generos
tplgen = pd.read_csv(tpl_file)
tplgen.rename(axis=1, mapper={'Genus':'Genero'}, inplace=True)
tax = tax.merge(tplgen, on='Genero', how='left')
tax.loc[tax.Family.notna() & (tax.Family != tax.Familia), 'Familia'] = tax.loc[tax.Family.notna() & (tax.Family != tax.Familia), 'Family']
tax.drop(axis=1, columns='Family', inplace=True)


# Corregir clasificacion de individuos clasificados a familia
famcha = {'Familia': {u'Bombacaceae': u'Malvaceae', u'Cecropiaceae': u'Urticaceae',
	u'Flacourtiaceae': u'Salicaceae', u'Hippocastanaceae': u'Sapindaceae',
	u'Hippocrateaceae': u'Celastraceae', u'Myrsinaceae': u'Primulaceae',
	u'Sterculiaceae': u'Malvaceae', u'Vivianiaceae': u'Francoaceae'}}
tax.replace(famcha, inplace=True)

# Fix Turpinia occdidentalis loop
if database == "Quimera":
	tax.loc[(tax.Genero == 'Staphylea') & (tax.Epiteto == 'occidentalis') &
		(tax.AutorEpiteto == 'Sw.'), 'SinonimoDe'] = None


# Single taxonomic pointer to indet individuals
indet = tax[tax.Familia.isna() & tax.Genero.isna() & tax.Epiteto.isna()]['TaxonID'].item()
tax.loc[(tax.Familia.isna() & tax.Genero.isna() & tax.Epiteto.notna()), 'SinonimoDe'] = indet

tax_count = int(tax.TaxonID.max())
# Single taxonomic pointers per family for individuals id to family
for fam in tax.Familia.unique():
	if pd.notna(fam):
		if len(tax[(tax.Familia == fam) & tax.Genero.isna() & tax.Epiteto.isna()]) == 0:
			tax_count += 1
			tax = tax.append({'TaxonID': tax_count, 'Familia': fam, 'Genero': None, 'Epiteto': None, 'Fuente': 1, 'FechaMod': pd.Timestamp.today()}, ignore_index=True)
		tax.loc[((tax.Familia == fam) & tax.Genero.isna() & tax.Epiteto.notna()), 'SinonimoDe'] = tax[(tax.Familia == fam) & tax.Genero.isna() & tax.Epiteto.isna()]['TaxonID'].item()

tax.to_sql("Taxonomia", conn, if_exists="replace", index = False)

# Corregir el error de numeracion de determinaciones en Quimera
if database == 'Quimera':
	inds = pd.read_sql_table(table_name='Individuos',con=conn)
	if inds.iloc[0].Dets == 0:
		inds.Dets += 1
		inds.to_sql("Individuos", conn, if_exists="replace", index = False, chunksize = 10000)


conn.close()
