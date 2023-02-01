import pandas as pd
import numpy as np
import os
import sqlite3
import shutil

BIOMEDIC = {'PRECIO UNIT. $', 'Código', 'DESCRIPCIÓN DEL PRODUCTO', 'TOTAL NETO REF.', 'CANTIDAD', 'Unidad de Manejo', 'Presentación por Bulto', 'FV', 'LABORATORIO', 'MÍNIMO DE COMPRA', 'LOTE'}
TIARES = {'Unidades x Bulto', 'F. V.', 'Pedido', 'Producto Farmacéutico', 'UDM', 'SUBTOTAL', 'PRECIO UNITARIO $', 'Foto Referencial', 'Descuento Promocional'}
KOTEICH = {'Total', 'Moneda', 'Descripcion', 'Precio', 'Marca', 'Codigo', 'Candad Solicitada'}
PLUS_MEDICAL = {'MONTO $', 'PRECIO POR PRESENTACION $', 'PEDIDO ', 'UNIDAD ', 'LABORATORIO', 'PRINCIPIO ACTIVO', 'CONDICION ', 'DESCRIPCIÓN', 'F. VENCIMIENTO', 'REGISTRO SANITARIO', 'PRECIO UNITARIO $'}
SAJJA_MEDIC = {'CÓDIGO', 'PRECIO X BLISTER/UNIDAD', 'Pedido ', 'Total', 'DESCRIPCIÓN DEL PRODUCTO', 'DATOS', 'FECHA DE VCTO.'}

PATHS = ['./temp/processed_csv', './temp/raw_csv']
'./temp/processed_excel'

def connect_to_db():
    # Connect to the database
    mydb = sqlite3.connect()
    # Create a cursor
    mycursor = mydb.cursor()
    # Return the cursor and the connection
    return mycursor, mydb

# Transform the raw data into a csv file
def transform_data():
    # Get raw data from ./Archivos
    raw_data = os.listdir('./Archivos')
    # Iterate over the raw data
    for file in raw_data:
        if file.endswith('.xlsx'):
            data = pd.read_excel(f'./Archivos/{file}', engine='openpyxl')
        elif file.endswith('.xls'):
            data = pd.read_excel(f'./Archivos/{file}', engine='xlrd')
        # Get file name
        file_name = name_drog(data, file.split('.')[0])
        if file_name != "No encontrado":
            # Save the data as a csv file in temp/csv folder
            data.to_csv(f'./temp/raw_csv/{file_name}.csv', index=False)
            # Move files from archivos to temp/processed_excel if file_name not "No encontrado"
            # os.rename(f'./Archivos/{file}', f'./temp/processed_excel/{file}')


def name_drog(data, name):
    data_iloc1 = set([x for x in data.iloc[1]])
    data_iloc5 = set([x for x in data.iloc[5]])
    data_iloc6 = set([x for x in data.iloc[6]])
    data_iloc7 = set([x for x in data.iloc[7]])
    data_iloc8 = set([x for x in data.iloc[8]])
    data_iloc9 = set([x for x in data.iloc[9]])
    data_iloc11 = set([x for x in data.iloc[11]])
    data_columns = set([x for x in data.columns])

    if TIARES.issubset(data_iloc1):
        return "Tiares"
    else:
        return "No encontrado"

def process_tiares():
    # Get raw data from ./temp/raw_csv/Tiares.csv
    data = pd.read_csv('./temp/raw_csv/Tiares.csv')
    # New headers
    new_headers = data.iloc[1]
    # Drop the first 6 rows
    data = data[2:]
    # Rename the headers
    data.columns = new_headers
    cols_to_use = ['Producto Farmacéutico', 'F. V.', 'PRECIO UNITARIO $', 'Descuento Promocional']
    data = data[cols_to_use]
    # Drop products agotados
    data = data[data['F. V.'] != 'Agotado']
    # Drop Nan price
    data.dropna(subset=['PRECIO UNITARIO $'], inplace=True)
    data['PRECIO UNITARIO $'] = data['PRECIO UNITARIO $'].str.replace(',', '.').astype(float)
    data['Descuento Promocional'] = data['Descuento Promocional'].str.replace(',', '.').astype(float)
    data['Descuento Promocional'] = data['Descuento Promocional'].replace(np.nan, 0)
    # Discount
    data['PRECIO UNITARIO $'] = data['PRECIO UNITARIO $'] - data['PRECIO UNITARIO $']*data['Descuento Promocional']
    data['PRECIO UNITARIO $'] = data['PRECIO UNITARIO $'].round(2)
    # Drop unnecessay cols
    # Drop the column 'OFERTAS'
    data = data.drop('F. V.', axis=1)
    # Drop the column 'existencia'
    data = data.drop('Descuento Promocional', axis=1)
    data.to_csv('./temp/processed_csv/Tiares.csv', index=False)
    


def process_cobeca():
    # Get raw data from ./temp/raw_csv/Cobeca.csv
    data = pd.read_csv('./temp/raw_csv/Cobeca.csv')
    # New headers
    new_headers = data.iloc[6]
    # Drop the first 6 rows
    data = data[7:]
    # Rename the headers
    data.columns = new_headers
    cols_to_use = ['Descripción del Artículo', 'Precio Mayoreo', 'OFERTAS', 'existencia', 'Cod. Ind.']
    data = data[cols_to_use]
    # Replace - with 0 in the column 'OFERTAS'
    data['OFERTAS'] = data['OFERTAS'].replace('-', 0)
    # Transform precio mayoreo and ofertas to float
    data['Precio Mayoreo'] = data['Precio Mayoreo'].str.replace(',', '.').astype(float)
    data['OFERTAS'] = data['OFERTAS'].str.replace('%', '')
    data['OFERTAS'] = data['OFERTAS'].str.replace(',', '.').astype(float)
    # if ofertas is empty, then ofertas = 0
    data['OFERTAS'] = data['OFERTAS'].replace(np.nan, 0)
    # If Precios Mayoreo is 0.01 or less, drop the row
    data = data[data['Precio Mayoreo'] > 0.99]
    # If existencia is 0, drop the row
    data = data[data['existencia'] != 0]
    # Precio Mayoreo * OFERTAS if OFERTAS is not 0 if OFERTAS is 0, Precio Mayoreo
    data['Precio Mayoreo'] = np.where(data['OFERTAS'] != 0, data['Precio Mayoreo'] - (data['Precio Mayoreo']*(data['OFERTAS']/100)), data['Precio Mayoreo'])
    data['Precio Mayoreo'] = data['Precio Mayoreo'] - data['Precio Mayoreo']*0.01
    # Round the column 'Precio Mayoreo' to 2 decimals
    data['Precio Mayoreo'] = data['Precio Mayoreo'].round(2)
    # Drop the column 'OFERTAS'
    data = data.drop('OFERTAS', axis=1)
    # Drop the column 'existencia'
    data = data.drop('existencia', axis=1)
    # Rename the columns
    data = data.rename(columns={'Cod. Ind.': 'Cod. Bar'})
    # Add column 'Proveedor'
    data['Proveedor'] = 'Cobeca'
    # Order by Descripción del Artículo
    data = data.sort_values(by=['Descripción del Artículo'])
    # Save the data as a csv file in temp/processed_csv folder
    data.to_csv('./temp/processed_csv/Cobeca.csv', index=False)

def process_dronena():
    # Get raw data from ./temp/raw_csv/Cobeca.csv
    data = pd.read_csv('./temp/raw_csv/Dronena.csv')
    cols_to_use = ['Descripción', 'Precio promo(Referencial)', 'Cód. barra']
    data = data[cols_to_use]
    # Rename the columns
    data = data.rename(columns={'Descripción': 'Descripción del Artículo', 'Precio promo(Referencial)': 'Precio Mayoreo', 'Cód. barra': 'Cod. Bar'})
    # Add column 'Proveedor'
    data['Proveedor'] = 'Dronena'
    # Save the data as a csv file in temp/processed_csv folder
    data.to_csv('./temp/processed_csv/Dronena.csv', index=False)

def process_dismeven():
    # Get raw data from ./temp/raw_csv/Dismeven.csv
    data = pd.read_csv('./temp/raw_csv/Dismeven.csv')
    # New headers
    new_headers = data.iloc[8]
    # Drop the first 9 rows
    data = data[9:]
    # Rename the headers
    data.columns = new_headers
    cols_to_use = ['DESCRIPCION PRODUCTO', ' EQUIVALENTE EN BS']
    data = data[cols_to_use]
    # Transform 'EQUIVALENTE EN BS' to float
    data[' EQUIVALENTE EN BS'] = data[' EQUIVALENTE EN BS'].str.replace(',', '.').astype(float)
    # Round the column 'EQUIVALENTE EN BS' to 2 decimals
    data[' EQUIVALENTE EN BS'] = data[' EQUIVALENTE EN BS'].round(2)
    # Rename the columns
    data = data.rename(columns={'DESCRIPCION PRODUCTO': 'Descripción del Artículo', ' EQUIVALENTE EN BS': 'Precio Mayoreo'})
    # Add column 'Proveedor'
    data['Proveedor'] = 'Dismeven'
    # Save the data as a csv file in temp/processed_csv folder
    data.to_csv('./temp/processed_csv/Dismeven.csv', index=False)

def process_distuca():
    # Get raw data from ./temp/raw_csv/Dismeven.csv
    data = pd.read_csv('./temp/raw_csv/Distuca.csv')
    # New headers
    new_headers = data.iloc[9]
    # Drop the first 9 rows
    data = data[10:]
    # Rename the headers
    data.columns = new_headers
    cols_to_use = ['DESCRIPCION', 'PRECIO BS', 'CODIGO DE BARRA']
    data = data[cols_to_use]
    data = data.dropna()
    # Transform 'Precio Final' to float
    data['PRECIO BS'] = data['PRECIO BS'].astype(float)
    # Round the column 'PRECIO BS' to 2 decimals
    data['PRECIO BS'] = data['PRECIO BS'].round(2)
    # Rename the columns
    data = data.rename(columns={'DESCRIPCION': 'Descripción del Artículo', 'PRECIO BS': 'Precio Mayoreo', 'CODIGO DE BARRA': 'Cod. Bar'})
    # Add column 'Proveedor'
    data['Proveedor'] = 'Distuca'
    # Save the data as a csv file in temp/processed_csv folder
    data.to_csv('./temp/processed_csv/Distuca.csv', index=False)

def process_drolanca():
    # Get raw data from ./temp/raw_csv/Drolanca.csv
    data = pd.read_csv('./temp/raw_csv/Drolanca.csv')
    # New headers    
    new_headers = data.iloc[5]
    # Drop the first 10 rows
    data = data[6:]
    # Rename the headers
    data.columns = new_headers
    cols_to_use = ['Descripción del Material', 'Precio Final ', 'Codigo de Barras']
    data = data[cols_to_use]
    # Transform 'Precio Final' to float
    data['Precio Final '] = data['Precio Final '].str.replace(',', '.').astype(float)
    data['Precio Final '] = data['Precio Final ']-data['Precio Final ']*0.04
    # Round the column 'Precio Final' to 2 decimals
    data['Precio Final '] = data['Precio Final '].round(2)
    # Rename the columns
    data = data.rename(columns={'Descripción del Material': 'Descripción del Artículo', 'Precio Final ': 'Precio Mayoreo', 'Codigo de Barras': 'Cod. Bar'})
    # Add column 'Proveedor'
    data['Proveedor'] = 'Drolanca'
    # Save the data as a csv file in temp/processed_csv folder
    data.to_csv('./temp/processed_csv/Drolanca.csv', index=False)

def process_gracitana_medicinas():
    # Get raw data from ./temp/raw_csv/Gracitana Medicinas.csv
    data = pd.read_csv('./temp/raw_csv/Gracitana Medicinas.csv')
    # New headers
    new_headers = data.iloc[11]
    # Drop the first 12 rows
    data = data[12:]
    # Rename the headers
    data.columns = new_headers
    cols_to_use = ['NOMBRE', 'PRECIO']
    data = data[cols_to_use]
    # Rename the columns
    data = data.rename(columns={'NOMBRE': 'Descripción del Artículo', 'PRECIO': 'Precio Mayoreo'})
    # Add column 'Proveedor'
    data['Proveedor'] = 'Gracitana Medicinas'
    # Save the data as a csv file in temp/processed_csv folder
    data.to_csv('./temp/processed_csv/Gracitana Medicinas.csv', index=False)

def process_gracitana_material_medico():
    # Get raw data from ./temp/raw_csv/Gracitana Material Medico.csv
    data = pd.read_csv('./temp/raw_csv/Gracitana Material Medico.csv')
    # New headers
    new_headers = data.iloc[11]
    # Drop the first 12 rows
    data = data[12:]
    # Rename the headers
    data.columns = new_headers
    cols_to_use = ['NOMBRE', 'PRECIO']
    data = data[cols_to_use]
    # Rename the columns
    data = data.rename(columns={'NOMBRE': 'Descripción del Artículo', 'PRECIO': 'Precio Mayoreo'})
    # Add column 'Proveedor'
    data['Proveedor'] = 'Gracitana Material Medico'
    # Save the data as a csv file in temp/processed_csv folder
    data.to_csv('./temp/processed_csv/Gracitana Material Medico.csv', index=False)

def process_insuaminca():
    # Get raw data from ./temp/raw_csv/Insuaminca.csv
    data = pd.read_csv('./temp/raw_csv/Insuaminca.csv')
    # New headers
    new_headers = data.iloc[8]
    # Drop the first 9 rows
    data = data[9:]
    # Rename the headers
    data.columns = new_headers
    cols_to_use = ['DESCRIPCION', 'PRECIO', 'CODBARRA']
    data = data[cols_to_use]
    # Transform 'PRECIO' to float
    data['PRECIO'] = data['PRECIO'].str.replace(',', '.').astype(float)
    # Get a connection to the database
    cursor, conn = connect_to_db()
    # Get tasa de cambio
    cursor.execute("SELECT precio_compra_moneda_nacional FROM tipo_moneda WHERE nombre_singular = 'DOLAR'")
    tasa_cambio = cursor.fetchone()[0]
    # Close the connection
    conn.close()
    # Transform 'PRECIO' to bolivares
    data['PRECIO'] = data['PRECIO'] * float(tasa_cambio)
    # Round the column 'PRECIO' to 2 decimals
    data['PRECIO'] = data['PRECIO'].round(2)
    # Rename the columns
    data = data.rename(columns={'DESCRIPCION': 'Descripción del Artículo', 'PRECIO': 'Precio Mayoreo', 'CODBARRA': 'Cod. Bar'})
    # Add column 'Proveedor'
    data['Proveedor'] = 'Insuaminca'
    # Save the data as a csv file in temp/processed_csv folder
    data.to_csv('./temp/processed_csv/Insuaminca.csv', index=False)

def process_vitalclinic():
    # Get raw data from ./temp/raw_csv/Vitalclinic.csv
    data = pd.read_csv('./temp/raw_csv/Vitalclinic.csv')
    # New headers
    new_headers = data.iloc[9]
    # Drop the first 10 rows
    data = data[10:]
    # Rename the headers
    data.columns = new_headers
    cols_to_use = ['DESCRIPCION', 'PRECIO', 'COD BARRAS']
    data = data[cols_to_use]
    # Drop duplicated columns
    data = data.loc[:,~data.columns.duplicated(keep='last')].copy()
    # Transform 'PRECIO' to float
    data['PRECIO'] = data['PRECIO'].str.replace(',', '.').astype(float)
    # Get a connection to the database
    cursor, conn = connect_to_db()
    # Get tasa de cambio
    cursor.execute("SELECT precio_compra_moneda_nacional FROM tipo_moneda WHERE nombre_singular = 'DOLAR'")
    tasa_cambio = cursor.fetchone()[0]
    # Close the connection
    conn.close()
    # Transform 'PRECIO' to bolivares
    data['PRECIO'] = data['PRECIO'] * float(tasa_cambio)
    # Round the column 'PRECIO' to 2 decimals
    data['PRECIO'] = data['PRECIO'].round(2)
    # Rename the columns
    data = data.rename(columns={'DESCRIPCION': 'Descripción del Artículo', 'PRECIO': 'Precio Mayoreo', 'COD BARRAS': 'Cod. Bar'})
    # Add column 'Proveedor'
    data['Proveedor'] = 'Vitalclinic'
    # Save the data as a csv file in temp/processed_csv folder
    data.to_csv('./temp/processed_csv/Vitalclinic.csv', index=False)

def process_drosalud():
    # Get raw data from ./temp/raw_csv/Drosalud.csv
    data = pd.read_csv('./temp/raw_csv/Drosalud.csv')
    # New headers
    new_headers = data.iloc[7]
    # Drop the first 10 rows
    data = data[8:]
    # Rename the headers
    data.columns = new_headers
    cols_to_use = ['Descripción', 'PRECIO']
    data = data[cols_to_use]
    # Transform 'PRECIO' to float
    data['PRECIO'] = data['PRECIO'].str.replace(',', '.').astype(float)
    # Get a connection to the database
    cursor, conn = connect_to_db()
    # Get tasa de cambio
    cursor.execute("SELECT precio_compra_moneda_nacional FROM tipo_moneda WHERE nombre_singular = 'DOLAR'")
    tasa_cambio = cursor.fetchone()[0]
    # Close the connection
    conn.close()
    # Transform 'PRECIO' to bolivares
    data['PRECIO'] = data['PRECIO'] * float(tasa_cambio)
    # Round the column 'PRECIO' to 2 decimals
    data['PRECIO'] = data['PRECIO'].round(2)
    # Rename the columns
    data = data.rename(columns={'Descripción': 'Descripción del Artículo', 'PRECIO': 'Precio Mayoreo'})
    # Add column 'Proveedor'
    data['Proveedor'] = 'Drosalud'
    # Save the data as a csv file in temp/processed_csv folder
    data.to_csv('./temp/processed_csv/Drosalud.csv', index=False)

def process_drolvilla_nacionales():
    # Get raw data from ./temp/raw_csv/Drolvilla_nacionales.csv
    data = pd.read_csv('./temp/raw_csv/Drolvilla Nacionales.csv')
    # new_headers = data.iloc[0]
    # # Drop the first 10 rows
    # data = data[1:]
    # # Rename the headers
    # data.columns = new_headers
    cols = ['nombre', 'precio']
    data = data[cols]
    # Rename the columns
    data = data.rename(columns={'nombre': 'Descripción del Artículo', 'precio': 'Precio Mayoreo'})
    # Get index where precio mayoreo = 'Sub - Total Factura:'
    index = data[data['Precio Mayoreo'] == 'Sub - Total Factura:'].index
    # Drop rows from index to the end
    data = data[:index[0]-1]
    # Add column 'Proveedor'
    # Transform 'PRECIO' to float
    data['Precio Mayoreo'] = data['Precio Mayoreo'].str.replace(',', '.').astype(float)
    data['Proveedor'] = 'Drolvilla Nacionales'
    # Save the data as a csv file in temp/processed_csv folder
    data.to_csv('./temp/processed_csv/Drolvilla Nacional.csv', index=False)

def process_drolvilla_importados():
    # Get raw data from ./temp/raw_csv/Drolvilla_importados.csv
    data = pd.read_csv('./temp/raw_csv/Drolvilla Importados.csv')
    # New headers
    new_headers = data.iloc[0]
    # Drop the first row
    data = data[1:]
    # Rename the headers
    data.columns = new_headers
    cols_to_use = ['MEDICINA IMPORTADA SOLO PAGO EN DOLARES', 'COSTO EN BOLIVARES PARA FACTURACION']
    data = data[cols_to_use]
    # Transform 'PRECIO' to float
    data['COSTO EN BOLIVARES PARA FACTURACION'] = data['COSTO EN BOLIVARES PARA FACTURACION'].str.replace(',', '.').astype(float)
    # Round the column 'PRECIO' to 2 decimals
    data['COSTO EN BOLIVARES PARA FACTURACION'] = data['COSTO EN BOLIVARES PARA FACTURACION'].round(2)
    # Rename the columns
    data = data.rename(columns={'MEDICINA IMPORTADA SOLO PAGO EN DOLARES': 'Descripción del Artículo', 'COSTO EN BOLIVARES PARA FACTURACION': 'Precio Mayoreo'})
    # Add column 'Proveedor'
    data['Proveedor'] = 'Drolvilla Importados'
    # Save the data as a csv file in temp/processed_csv folder
    data.to_csv('./temp/processed_csv/Drolvilla Importado.csv', index=False)

def process_unipharma():
    # Get raw data from ./temp/raw_csv/Unipharma.csv
    data = pd.read_csv('./temp/raw_csv/Unipharma.csv')
    # New headers
    new_headers = data.iloc[8]
    # Drop the first row
    data = data[9:]
    # Rename the headers
    data.columns = new_headers
    cols = ['DESCRIPCION', -0.05, 'CODIGO']
    data = data[cols]
    # Rename the columns
    data = data.rename(columns={'DESCRIPCION': 'Descripción del Artículo', -0.05: 'Precio Mayoreo', 'CODIGO': 'Cod. Bar'})
    # Drop rows where 'Precio Mayoreo' is 'NaN' or empty
    data = data.dropna(subset=['Precio Mayoreo'])
    # Transform 'PRECIO' to float
    data['Precio Mayoreo'] = data['Precio Mayoreo'].astype(float)
    # Connect to the database
    cursor, conn = connect_to_db()
    # Get tasa de cambio
    cursor.execute("SELECT precio_compra_moneda_nacional FROM tipo_moneda WHERE nombre_singular = 'DOLAR'")
    tasa_cambio = cursor.fetchone()[0]
    # Close the connection
    conn.close()
    # Transform 'PRECIO' to bolivares
    data['Precio Mayoreo'] = data['Precio Mayoreo'] * float(tasa_cambio)
    # Round the column 'PRECIO' to 2 decimals
    data['Precio Mayoreo'] = data['Precio Mayoreo'].round(2)
    # Add column 'Proveedor'
    data['Proveedor'] = 'Unipharma'
    # Save the data as a csv file in temp/processed_csv folder
    data.to_csv('./temp/processed_csv/Unipharma.csv', index=False)

def prepare_final_csv(method='off'):
    for folder in PATHS:
        delete_content_folder(folder)

    transform_data()
    if os.path.exists('./temp/raw_csv/'):
        list_not_found = []
        if not os.listdir('./temp/raw_csv/'):
            return Exception('No se encontraron archivos en la carpeta ./temp/raw_csv/')
        # Get all the files in temp/raw_csv folder
        files = os.listdir('./temp/raw_csv/')
        # Loop through the files
        for file in files:
            # Get the name of the file
            file_name = file.split('.')[0]
            # Call the function that matches the file name
            if file_name == 'Gracitana Medicinas':
                process_gracitana_medicinas()
            elif file_name == 'Gracitana Material Medico':
                process_gracitana_material_medico()
            elif file_name == 'Insuaminca':
                process_insuaminca()
            elif file_name == 'Vitalclinic':
                process_vitalclinic()
            elif file_name == 'Cobeca':
                process_cobeca()
            elif file_name == 'Drolanca':
                process_drolanca()
            elif file_name == 'Dismeven':
                process_dismeven()
            elif file_name == 'Drosalud':
                process_drosalud()
            elif file_name == 'Drolvilla Nacionales':
                process_drolvilla_nacionales()
            elif file_name == 'Drolvilla Importados':
                process_drolvilla_importados()
            elif file_name == 'Unipharma':
                process_unipharma()
            elif file_name == 'Dronena':
                process_dronena()
            elif file_name == 'Distuca':
                process_distuca()
            else:
                list_not_found.append(file_name)
    # If not files in ('./temp/processed_csv/') folder break the function
    if not os.listdir('./temp/processed_csv/'):
        return Exception('No se encontraron archivos en la carpeta ./temp/processed_csv/')
    # Get all the csv files in temp/processed_csv folder
    files = os.listdir('./temp/processed_csv/')
    # Create a list to store the dataframes
    list_df = []
    # Loop through the files
    for file in files:
        # Read the csv file
        df = pd.read_csv('./temp/processed_csv/' + file)
        # Append the dataframe to the list
        list_df.append(df)
    # Concatenate all the dataframes in the list
    data = pd.concat(list_df, axis=0)
    # Drop nan rows
    data = data.dropna(subset=['Descripción del Artículo', 'Precio Mayoreo'])
    # Drop rows where Precios Mayoreo is 'PRECIO'
    data = data[data['Precio Mayoreo'] != 'PRECIO']
    if method == 'off':
        # Save the data as a csv file in temp/final_csv folder
        data.to_csv('./temp/final_csv.csv', index=False)
    elif method == 'on':
        # Read final_csv
        final_df = pd.read_csv('./temp/final_csv.csv')
        # Concat data with final_csv
        data = pd.concat([final_df, data], axis=0)
        # Drop duplicates
        #data.drop_duplicates(subset=['Cod. Bar'], keep='last', inplace=True)
        data.drop_duplicates(subset=['Descripción del Artículo', 'Proveedor'], keep='last', inplace=True)
        # Save the data as a csv file in temp/final_csv folder
        data.to_csv('./temp/final_csv.csv', index=False)

    for folder in PATHS:
        delete_content_folder(folder)

def delete_content_folder(folder):
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))

process_tiares()