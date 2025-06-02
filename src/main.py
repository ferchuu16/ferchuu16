import flet as ft

PRODUCTOS = {
    "Gaseosa 500ml": 500,
    "Galletitas": 350,
    "Alfajor": 400,
    "Jugo": 300,
    "Caramelos": 100,
    "Papitas": 450
}

ventas = []

def main(page: ft.Page):
    page.title = "Kiosco Escolar"
    page.scroll = ft.ScrollMode.AUTO
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = "#E3F2FD"  # Azul claro (antes era ft.colors.LIGHT_BLUE_50)

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
    total_label = ft.Text(value="Total: $0.00", style="headlineSmall", color="#2E7D32")  # Verde oscuro

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

    def agregar_venta(e):
        if not selected_product.value or not cantidad.value:
            return

        producto = selected_product.value
        cant = int(cantidad.value)
        precio = PRODUCTOS[producto]
        subtotal = cant * precio

        ventas.append((producto, cant, precio, subtotal))

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

        total = sum(v[3] for v in ventas)
        total_label.value = f"Total: ${total:.2f}"
        page.update()

    selected_product.on_change = actualizar_precio

    page.add(
        ft.Column([
            ft.Text("Kiosco Automatizado", style="headlineMedium", color="#0D47A1"),  # Azul fuerte
            ft.Row([selected_product, cantidad, precio_field]),
            ft.ElevatedButton(
                "Agregar Venta",
                on_click=agregar_venta,
                bgcolor="#1976D2",  # Azul botón
                color="white"
            ),
            tabla,
            total_label
        ],
        spacing=20,
        expand=True)
    )

ft.app(target=main)
