"""
export_excel.py - Exporta los resultados JSON a Excel con formato profesional.

USO:
    python export_excel.py

SALIDA:
    data/contactos_municipales.xlsx
"""

import json
import os
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter


def main():
    # Cargar datos
    with open('data/results.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Crear workbook
    wb = Workbook()
    ws = wb.active
    ws.title = 'Contactos Municipales'

    # Estilos
    header_fill = PatternFill(start_color='1F4E79', end_color='1F4E79', fill_type='solid')
    header_font = Font(bold=True, color='FFFFFF', size=11)
    alt_fill = PatternFill(start_color='D6EAF8', end_color='D6EAF8', fill_type='solid')
    thin_border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )

    # Headers
    headers = ['Municipio', 'URL Municipio', 'Nombre', 'Cargo', 'Partido', 'Email', 'Tipo', 'Source URL']
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal='center', vertical='center')
        cell.border = thin_border

    # Congelar cabecera
    ws.freeze_panes = 'A2'

    # Datos
    row = 2
    for muni in data:
        municipality = muni.get('municipality', '')
        url = muni.get('url', '')
        contacts = muni.get('data', [])

        if contacts:
            for contact in contacts:
                ws.cell(row=row, column=1, value=municipality)
                ws.cell(row=row, column=2, value=url)
                ws.cell(row=row, column=3, value=contact.get('nombre', ''))
                ws.cell(row=row, column=4, value=contact.get('cargo', ''))
                ws.cell(row=row, column=5, value=contact.get('partido', ''))
                ws.cell(row=row, column=6, value=contact.get('email', ''))
                ws.cell(row=row, column=7, value=contact.get('tipo', ''))
                ws.cell(row=row, column=8, value=contact.get('source_url', ''))

                for col in range(1, 9):
                    cell = ws.cell(row=row, column=col)
                    cell.border = thin_border
                    cell.alignment = Alignment(vertical='center', wrap_text=True)
                    if row % 2 == 0:
                        cell.fill = alt_fill
                row += 1
        else:
            ws.cell(row=row, column=1, value=municipality)
            ws.cell(row=row, column=2, value=url)
            ws.cell(row=row, column=3, value='(Sin contactos encontrados)')
            for col in range(1, 9):
                cell = ws.cell(row=row, column=col)
                cell.border = thin_border
                cell.alignment = Alignment(vertical='center')
                if row % 2 == 0:
                    cell.fill = alt_fill
            row += 1

    # Ajustar anchos de columna
    col_widths = [25, 35, 40, 50, 15, 30, 25, 60]
    for i, width in enumerate(col_widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = width

    # Guardar
    output_dir = 'data/exports'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    output_path = os.path.join(output_dir, 'contactos_municipales.xlsx')
    wb.save(output_path)
    print(f'Excel generado: {output_path}')
    print(f'Total filas de datos: {row - 1}')


if __name__ == '__main__':
    main()
