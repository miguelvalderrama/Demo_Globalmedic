import pandas as pd
import numpy as np
import os
import PyPDF2
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
    data_iloc1 = set(x for x in data.iloc[1])
    data_iloc6 = set(x for x in data.iloc[6])
    data_iloc10 = set(x for x in data.iloc[10])
    data_iloc20 = set(x for x in data.iloc[20])

    if TIARES.issubset(data_iloc1):
        return "Tiares"
    elif KOTEICH.issubset(data_iloc6):
        return "Koteich"
    elif BIOMEDIC.issubset(data_iloc10):
        return "Biomedic"
    elif SAJJA_MEDIC.issubset(data_iloc20):
        return "Sajja_Medic"
    elif PLUS_MEDICAL.issubset(data_iloc20):
        return "Plus_Medical"
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
    data['Producto Farmacéutico'] = data['Producto Farmacéutico'].str.replace('\n', ' ')
    data['PRECIO UNITARIO $'] = data['PRECIO UNITARIO $'].str.replace(',', '.').astype(float)
    data['Descuento Promocional'] = data['Descuento Promocional'].str.replace(',', '.').astype(float)
    data['Descuento Promocional'] = data['Descuento Promocional'].replace(np.nan, 0)
    # Discount
    data['PRECIO UNITARIO $'] = data['PRECIO UNITARIO $'] - data['PRECIO UNITARIO $']*data['Descuento Promocional']
    data['PRECIO UNITARIO $'] = data['PRECIO UNITARIO $'].round(2)
    # Drop unnecessay cols
    data.dropna(subset=['F. V.'], inplace=True)
    # Drop the column 'OFERTAS'
    data = data.drop('F. V.', axis=1)
    # Drop the column 'existencia'
    data = data.drop('Descuento Promocional', axis=1)
    data = data.rename(columns={'Producto Farmacéutico': 'Descripcion', 'PRECIO UNITARIO $': 'Precio'})
    data['Proveedor'] = 'Tiares'
    # Save the data as a csv file in temp/processed_csv folder
    data.to_csv('./temp/processed_csv/Tiares.csv', index=False)
    
def process_biomedic():
    # Get raw data from ./temp/raw_csv/Biomedic.csv
    data = pd.read_csv('./temp/raw_csv/Biomedic.csv')
    # New headers
    new_headers = data.iloc[10]
    # Drop the first 6 rows
    data = data[11:]
    # Rename the headers
    data.columns = new_headers
    cols_to_use = ['DESCRIPCIÓN DEL PRODUCTO', 'PRECIO UNIT. $']
    data = data[cols_to_use]
    data = data.rename(columns={'DESCRIPCIÓN DEL PRODUCTO': 'Descripcion', 'PRECIO UNIT. $': 'Precio'})
    data.dropna(subset=['Precio'], inplace=True)
    data['Proveedor'] = 'Biomedic'
    # Save the data as a csv file in temp/processed_csv folder
    data.to_csv('./temp/processed_csv/Biomedic.csv', index=False)

def process_koteich():
    # Get raw data from ./temp/raw_csv/Koteich.csv
    data = pd.read_csv('./temp/raw_csv/Koteich.csv')
    # New headers
    new_headers = data.iloc[6]
    # Drop the first 6 rows
    data = data[7:]
    # Rename the headers
    data.columns = new_headers
    cols_to_use = ['Descripcion', 'Precio']
    data = data[cols_to_use]
    data.dropna(subset=['Precio'], inplace=True)
    data['Proveedor'] = 'Marquez y Koteich'
    # Save the data as a csv file in temp/processed_csv folder
    data.to_csv('./temp/processed_csv/Koteich.csv', index=False)

def process_sajja():
    # Get raw data from ./temp/raw_csv/Sajja_Medic.csv
    data = pd.read_csv('./temp/raw_csv/Sajja_Medic.csv')
    # New headers
    new_headers = data.iloc[20]
    # Drop the first 6 rows
    data = data[21:]
    # Rename the headers
    data.columns = new_headers
    cols_to_use = ['DESCRIPCIÓN DEL PRODUCTO', 'PRECIO X BLISTER/UNIDAD']
    data = data[cols_to_use]
    data = data.rename(columns={'DESCRIPCIÓN DEL PRODUCTO': 'Descripcion', 'PRECIO X BLISTER/UNIDAD': 'Precio'})
    data.dropna(subset=['Precio'], inplace=True)
    data['Proveedor'] = 'Sajja Medic'
    # Save the data as a csv file in temp/processed_csv folder
    data.to_csv('./temp/processed_csv/Sajja_Medic.csv', index=False)
    
def process_plus_medical():
    # Get raw data from ./temp/raw_csv/Plus_Medical.csv
    data = pd.read_csv('./temp/raw_csv/Plus_Medical.csv')
    # New headers
    new_headers = data.iloc[20]
    # Drop the first 6 rows
    data = data[21:]
    # Rename the headers
    data.columns = new_headers
    cols_to_use = ['DESCRIPCIÓN', 'PRECIO UNITARIO $']
    data = data[cols_to_use]
    data = data.rename(columns={'DESCRIPCIÓN': 'Descripcion', 'PRECIO UNITARIO $': 'Precio'})
    data.dropna(subset=['Precio'], inplace=True)
    data['Proveedor'] = 'Plus Medical'
    # Save the data as a csv file in temp/processed_csv folder
    data.to_csv('./temp/processed_csv/Plus_Medical.csv', index=False)

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
            if file_name == 'Tiares':
                process_tiares()
            elif file_name == 'Biomedic':
                process_biomedic()
            elif file_name == 'Koteich':
                process_koteich()
            elif file_name == 'Plus_Medical':
                process_plus_medical()
            elif file_name == 'Sajja_Medic':
                process_sajja()
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
    data = data.dropna(subset=['Descripcion', 'Precio'])
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
        data.drop_duplicates(subset=['Descripcion', 'Precio'], keep='last', inplace=True)
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
