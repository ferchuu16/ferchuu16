import flet as ft
import csv
import os

PRODUCTOS = {
    "Gaseosa 500ml": 500,
    "Galletitas": 350,
    "Alfajor": 400,
    "Jugo": 300,
    "Caramelos": 100,
    "Papitas": 450
}

ventas = []
CSV_FILE = "ventas.csv"

def guardar_en_csv(venta):
    with open(CSV_FILE, mode="a", newline="") as archivo:
        escritor = csv.writer(archivo)
        escritor.writerow(venta)

def reescribir_csv():
    with open(CSV_FILE, mode="w", newline="") as archivo:
        escritor = csv.writer(archivo)
        for v in ventas:
            escritor.writerow(v)

def cargar_ventas():
    if not os.path.exists(CSV_FILE):
        return []
    with open(CSV_FILE, mode="r") as archivo:
        lector = csv.reader(archivo)
        return [ (fila[0], int(fila[1]), int(fila[2]), int(fila[3])) for fila in lector ]

def main(page: ft.Page):
    page.title = "Kiosco Escolar"
    page.scroll = ft.ScrollMode.AUTO
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = "#E3F2FD"

    selected_product = ft.Dropdown(
        label="Producto",
        options=[ft.dropdown.Option(p) for p in PRODUCTOS],
        width=300
    )

    cantidad = ft.Dropdown(
        label="Cantidad",
        options=[ft.dropdown.Option(str(i)) for i in range(1, 11)],
        width=150
    )

    precio_field = ft.TextField(label="Precio Unitario", read_only=True, width=200)
    total_label = ft.Text(value="Total: $0.00", style="headlineSmall", color="#2E7D32")

    historial_text = ft.Text(value="", selectable=True)

    tabla = ft.DataTable(
        columns=[
            ft.DataColumn(label=ft.Text("Producto")),
            ft.DataColumn(label=ft.Text("Cantidad")),
            ft.DataColumn(label=ft.Text("Precio")),
            ft.DataColumn(label=ft.Text("Subtotal")),
        ],
        rows=[]
    )

    def actualizar_precio(e):
        producto = selected_product.value
        if producto:
            precio = PRODUCTOS[producto]
            precio_field.value = str(precio)
            page.update()

    def actualizar_tabla():
        tabla.rows.clear()
        for venta in ventas:
            producto, cant, precio, subtotal = venta
            tabla.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(producto)),
                        ft.DataCell(ft.Text(str(cant))),
                        ft.DataCell(ft.Text(f"${precio}")),
                        ft.DataCell(ft.Text(f"${subtotal}")),
                    ]
                )
            )
        total_label.value = f"Total: ${sum(v[3] for v in ventas):.2f}"
        page.update()

    def agregar_venta(e):
        if not selected_product.value or not cantidad.value:
            return

        producto = selected_product.value
        cant = int(cantidad.value)
        precio = PRODUCTOS[producto]
        subtotal = cant * precio

        venta = (producto, cant, precio, subtotal)
        ventas.append(venta)
        guardar_en_csv(venta)
        actualizar_tabla()

    def borrar_ultima_venta(e):
        if ventas:
            ventas.pop()
            reescribir_csv()
            actualizar_tabla()

    def borrar_todo(e):
        ventas.clear()
        if os.path.exists(CSV_FILE):
            os.remove(CSV_FILE)
        actualizar_tabla()

    def mostrar_historial(e):
        texto = ""
        for i, v in enumerate(ventas, 1):
            texto += f"{i}. {v[0]} x{v[1]} - ${v[3]}\n"
        historial_text.value = texto or "Sin ventas registradas."
        page.update()

   


    selected_product.on_change = actualizar_precio

    # Cargar ventas guardadas
    ventas.extend(cargar_ventas())
    actualizar_tabla()

    page.add(
        ft.Column([
            ft.Text("Kiosco Automatizado", style="headlineMedium", color="#0D47A1"),
            ft.Row([selected_product, cantidad, precio_field]),
            ft.Row([
                ft.ElevatedButton("Agregar Venta", on_click=agregar_venta, bgcolor="#1976D2", color="white"),
                ft.ElevatedButton("Borrar Última", on_click=borrar_ultima_venta, bgcolor="#F55A00", color="white"),
               ft.ElevatedButton("Borrar Todo", on_click=lambda e: mostrar_confirmacion(), bgcolor="#C62828", color="white"),
                ft.ElevatedButton("Mostrar Historial", on_click=mostrar_historial, bgcolor="#0C0D0D", color="white")
            ], spacing=10),
            tabla,
            total_label,
            ft.Text("Historial de Ventas:", style="titleMedium", color="#004D40"),
            historial_text
        ], spacing=20)
    )


    dialogo_confirmacion = ft.AlertDialog(
    modal=True,
    title=ft.Text("¿Estás seguro?"),
    content=ft.Text("Esto borrará TODAS las ventas. No se puede deshacer."),
    actions=[
        ft.TextButton("Cancelar", on_click=lambda e: page.dialog.dismiss()),
        ft.TextButton("Borrar Todo", style=ft.ButtonStyle(bgcolor="#D32F2F", color="white"), on_click=lambda e: confirmar_borrado()),
    ]
    )
    def confirmar_borrado():
        ventas.clear()
    if os.path.exists(CSV_FILE):
        os.remove(CSV_FILE)
    actualizar_tabla()
    page.dialog = None
    page.update()

    def mostrar_confirmacion():
     page.dialog = dialogo_confirmacion
    dialogo_confirmacion.open = True
    page.update()

    



ft.app(target=main)
