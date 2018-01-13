"""
Final taxonomic updates for databases. Assumes database `Quimera` was loaded from
backup file `Quimera_20180110.sql` and database `IFN` from `IFN_20180112.sql`.
"""
import sqlalchemy as al
import pandas as pd

user = ""
password = ""
database = ""

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

################################################
# 		Corregir clasificacion de generos
#################################################

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

conn.close()
