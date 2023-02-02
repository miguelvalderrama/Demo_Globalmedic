import pandas as pd

BIOMEDIC = {'PRECIO UNIT. $', 'Código', 'DESCRIPCIÓN DEL PRODUCTO', 'TOTAL NETO REF.', 'CANTIDAD', 'Unidad de Manejo', 'Presentación por Bulto', 'FV', 'LABORATORIO', 'MÍNIMO DE COMPRA', 'LOTE'}
TIARES = {'Unidades x Bulto', 'F. V.', 'Pedido', 'Producto Farmacéutico', 'UDM', 'SUBTOTAL', 'PRECIO UNITARIO $', 'Foto Referencial', 'Descuento Promocional'}
KOTEICH = {'Total', 'Moneda', 'Descripcion', 'Precio', 'Marca', 'Codigo', 'Candad Solicitada'}
PLUS_MEDICAL = {'MONTO $', 'PRECIO POR PRESENTACION $', 'PEDIDO ', 'UNIDAD ', 'LABORATORIO', 'PRINCIPIO ACTIVO', 'CONDICION ', 'DESCRIPCIÓN', 'F. VENCIMIENTO', 'REGISTRO SANITARIO', 'PRECIO UNITARIO $'}
SAJJA_MEDIC = {'CÓDIGO', 'PRECIO X BLISTER/UNIDAD', 'Pedido ', 'Total', 'DESCRIPCIÓN DEL PRODUCTO', 'DATOS', 'FECHA DE VCTO.'}


df = pd.read_excel('./Pruebas/$ DISTRIBUIDORES Mcy 10-01-2023 BIOMEDIC LAB.xlsx', engine='openpyxl')
data_iloc = set(x for x in df.iloc[10])
# print(data_iloc.difference(distuca))
# print(distuca.difference(data_iloc))
df.to_csv('Try.csv')