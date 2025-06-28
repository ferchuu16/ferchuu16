import flet as ft
import csv
import os

# --- DEFINICIONES DE ARCHIVOS ---
# Define los nombres de archivo para los datos de ventas y productos
SALES_CSV_FILE = "ventas.csv"
PRODUCTS_CSV_FILE = "productos.csv"

# --- ESTRUCTURAS DE DATOS GLOBALES ---
# Se llenarán desde los archivos CSV al iniciar
PRODUCTOS = {}
ventas = []

# ===============================================================
# FUNCIONES PARA MANEJAR DATOS DE PRODUCTOS (Persistencia)
# ===============================================================

def cargar_productos():
    """
    Carga los productos desde PRODUCTS_CSV_FILE al diccionario global PRODUCTOS.
    Si el archivo no existe, lo llena con productos por defecto.
    """
    global PRODUCTOS
    # Productos por defecto en caso de que falte el CSV
    default_products = {
        "Gaseosa 500ml": 500,
        "Galletitas": 350,
        "Alfajor": 400,
        "Jugo": 300,
        "Caramelos": 100,
        "Papitas": 450
    }

    if not os.path.exists(PRODUCTS_CSV_FILE):
        # Si el archivo no existe, usa los valores por defecto y crea el archivo
        PRODUCTOS = default_products
        guardar_productos()
    else:
        # Si el archivo existe, lee de él
        try:
            with open(PRODUCTS_CSV_FILE, mode='r', newline='', encoding='utf-8') as archivo:
                lector = csv.reader(archivo)
                # Maneja un posible archivo vacío o malformado
                productos_cargados = {fila[0]: int(fila[1]) for fila in lector if fila}
                if not productos_cargados: # Si está vacío después de leer
                    PRODUCTOS = default_products
                    guardar_productos()
                else:
                    PRODUCTOS = productos_cargados
        except (IOError, IndexError, ValueError):
            # Si hay cualquier error, resetea con los valores por defecto
            PRODUCTOS = default_products
            guardar_productos()

def guardar_productos():
    """
    Guarda el estado actual del diccionario PRODUCTOS en PRODUCTS_CSV_FILE.
    Esta función sobrescribe el archivo completamente con los nuevos datos.
    """
    with open(PRODUCTS_CSV_FILE, mode='w', newline='', encoding='utf-8') as archivo:
        escritor = csv.writer(archivo)
        for producto, precio in PRODUCTOS.items():
            escritor.writerow([producto, precio])

# ===============================================================
# FUNCIONES PARA MANEJAR DATOS DE VENTAS (Persistencia)
# ===============================================================

def guardar_en_csv(venta):
    """Añade una única venta al archivo CSV de ventas."""
    with open(SALES_CSV_FILE, mode="a", newline="", encoding='utf-8') as archivo:
        escritor = csv.writer(archivo)
        escritor.writerow(venta)

def reescribir_csv():
    """Reescribe todo el archivo CSV de ventas con la lista de ventas actual."""
    with open(SALES_CSV_FILE, mode="w", newline="", encoding='utf-8') as archivo:
        escritor = csv.writer(archivo)
        for v in ventas:
            escritor.writerow(v)

def cargar_ventas():
    """Carga las ventas desde el archivo CSV a la lista global de ventas."""
    if not os.path.exists(SALES_CSV_FILE):
        return []
    with open(SALES_CSV_FILE, mode="r", encoding='utf-8') as archivo:
        lector = csv.reader(archivo)
        loaded_ventas = []
        for fila in lector:
            # Validación básica para la estructura de la fila
            if len(fila) == 4:
                try:
                    # Convierte los datos a los tipos correctos
                    loaded_ventas.append((fila[0], int(fila[1]), int(fila[2]), int(fila[3])))
                except (ValueError, IndexError):
                    print(f"Omitiendo fila malformada en el CSV de ventas: {fila}")
        return loaded_ventas

# ===============================================================
# FUNCIÓN PRINCIPAL DE LA APLICACIÓN
# ===============================================================
def main(page: ft.Page):
    page.title = "Kiosco Escolar Re Piola"
    page.scroll = ft.ScrollMode.ADAPTIVE
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = "#FFF3E0"
    page.window_width = 800
    page.window_height = 900
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    
    # --- CARGA INICIAL DE DATOS ---
    cargar_productos()
    ventas.extend(cargar_ventas())

    # --- COMPONENTES DE LA INTERFAZ ---
    snackbar = ft.SnackBar(content=ft.Text(""), bgcolor="#4CAF50", show_close_icon=True)
    page.overlay.append(snackbar)

    selected_product = ft.Dropdown(label="Producto", width=300, border_color="#FFB74D")
    cantidad = ft.Dropdown(label="Cantidad", options=[ft.dropdown.Option(str(i)) for i in range(1, 11)], width=150, border_color="#FFB74D")
    precio_field = ft.TextField(label="Precio Unitario", read_only=True, width=200, border_color="#FFB74D")
    total_label = ft.Text(value="Total: $0.00", size=20, weight=ft.FontWeight.BOLD, color="#388E3C")

    nuevo_producto = ft.TextField(label="Nombre Nuevo Producto", width=300, border_color="#9C27B0")
    nuevo_precio = ft.TextField(label="Precio", keyboard_type=ft.KeyboardType.NUMBER, width=150, border_color="#9C27B0")
    
    producto_modificar = ft.Dropdown(label="Seleccionar Producto", width=300, border_color="#FBC02D")
    nuevo_precio_modificado = ft.TextField(label="Nuevo Precio", keyboard_type=ft.KeyboardType.NUMBER, width=150, border_color="#FBC02D")

    tabla = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Producto")),
            ft.DataColumn(ft.Text("Cantidad"), numeric=True),
            ft.DataColumn(ft.Text("Precio Unit."), numeric=True),
            ft.DataColumn(ft.Text("Subtotal"), numeric=True),
        ],
        rows=[],
        border=ft.border.all(1, "#E0E0E0"),
        border_radius=ft.border_radius.all(10),
        heading_row_color="#FFF3E0",
    )
    
    # --- FUNCIONES LÓGICAS DEL NÚCLEO ---
    def mostrar_mensaje(texto, color="#4CAF50"):
        snackbar.content.value = texto
        snackbar.bgcolor = color
        snackbar.open = True
        page.update()

    def actualizar_dropdowns():
        """Actualiza las opciones en todos los menús desplegables de productos."""
        product_options = [ft.dropdown.Option(p) for p in sorted(PRODUCTOS.keys())]
        selected_product.options = product_options
        producto_modificar.options = product_options

    def actualizar_precio(e):
        """Actualiza el campo de precio cuando se selecciona un producto."""
        producto = selected_product.value
        if producto and producto in PRODUCTOS:
            precio_field.value = str(PRODUCTOS[producto])
        else:
            precio_field.value = ""
        # *** FIX: Se necesita actualizar la página para que el cambio sea visible ***
        page.update()

    def actualizar_tabla():
        """Limpia y reconstruye la tabla de datos de ventas."""
        tabla.rows.clear()
        total_ventas = sum(v[3] for v in ventas)
        for producto, cant, precio, subtotal in ventas:
            tabla.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(producto)),
                    ft.DataCell(ft.Text(str(cant))),
                    ft.DataCell(ft.Text(f"${precio}")),
                    ft.DataCell(ft.Text(f"${subtotal}")),
                ])
            )
        total_label.value = f"Total: ${total_ventas:.2f}"

    # --- MANEJADORES DE EVENTOS ---
    def agregar_venta(e):
        if not selected_product.value or not cantidad.value:
            mostrar_mensaje("Seleccioná un producto y cantidad.", "#FFC107")
            return
        
        producto = selected_product.value
        cant = int(cantidad.value)
        precio = PRODUCTOS.get(producto, 0)
        subtotal = cant * precio
        
        venta = (producto, cant, precio, subtotal)
        ventas.append(venta)
        guardar_en_csv(venta)
        
        actualizar_tabla()
        mostrar_mensaje(f"Venta agregada: {producto} x{cant}.")
        selected_product.value = None
        cantidad.value = None
        precio_field.value = ""
        page.update()

    def agregar_producto(e):
        nombre = nuevo_producto.value.strip()
        precio_str = nuevo_precio.value.strip()
        
        if not nombre or not precio_str:
            mostrar_mensaje("El nombre y el precio no pueden estar vacíos.", "#FF5722")
            return
        
        if nombre in PRODUCTOS:
            mostrar_mensaje(f"El producto '{nombre}' ya existe.", "#FF9800")
            return

        try:
            precio = int(precio_str)
            if precio <= 0: raise ValueError
        except ValueError:
            mostrar_mensaje("El precio debe ser un número positivo.", "#FF5722")
            return
            
        PRODUCTOS[nombre] = precio
        guardar_productos()
        
        nuevo_producto.value = ""
        nuevo_precio.value = ""
        actualizar_dropdowns() # Actualiza los datos de los dropdowns
        mostrar_mensaje(f"Producto agregado: {nombre} (${precio})")
        # *** FIX: Llama a page.update() para mostrar los cambios en los dropdowns ***
        page.update()

    def modificar_precio(e):
        prod = producto_modificar.value
        nuevo_precio_str = nuevo_precio_modificado.value.strip()

        if not prod or not nuevo_precio_str:
            mostrar_mensaje("Selecciona un producto e ingresa un nuevo precio.", "#FF5722")
            return
            
        try:
            nuevo_p = int(nuevo_precio_str)
            if nuevo_p <= 0: raise ValueError
        except ValueError:
            mostrar_mensaje("El nuevo precio debe ser un número positivo.", "#FF5722")
            return

        PRODUCTOS[prod] = nuevo_p
        guardar_productos()
        
        nuevo_precio_modificado.value = ""
        producto_modificar.value = None
        actualizar_dropdowns()
        mostrar_mensaje(f"Precio modificado: {prod} ahora vale ${nuevo_p}.")
        page.update()

    def borrar_producto(e):
        prod = producto_modificar.value
        if not prod:
            mostrar_mensaje("Selecciona un producto para eliminar.", "#FF5722")
            return
            
        if any(v[0] == prod for v in ventas):
            mostrar_mensaje("No se puede borrar: hay ventas registradas con ese producto.", "#FF9800")
            return
            
        del PRODUCTOS[prod]
        guardar_productos()
        
        producto_modificar.value = None
        actualizar_dropdowns() # Actualiza los datos de los dropdowns
        mostrar_mensaje(f"Producto eliminado: {prod}.", "#F44336")
        # *** FIX: Llama a page.update() para mostrar los cambios en los dropdowns ***
        page.update()

    def borrar_ultima_venta(e):
        if ventas:
            ultima = ventas.pop()
            reescribir_csv()
            actualizar_tabla()
            mostrar_mensaje(f"Venta borrada: {ultima[0]} x{ultima[1]}", "#F44336")
            page.update()
        else:
            mostrar_mensaje("No hay ventas para borrar.", "#FF5722")

    def confirmar_borrado_ventas(e):
        dialogo_confirmacion.open = False
        ventas.clear()
        if os.path.exists(SALES_CSV_FILE):
            os.remove(SALES_CSV_FILE)
        actualizar_tabla()
        mostrar_mensaje("Todas las ventas fueron borradas.", "#F89809")
        page.update()

    def cerrar_dialogo(e):
        dialogo_confirmacion.open = False
        page.update()

    dialogo_confirmacion = ft.AlertDialog(
        modal=True,
        title=ft.Text("¿Estás seguro?"),
        content=ft.Text("Esto borrará TODAS las ventas permanentemente. No se puede deshacer."),
        actions=[
            ft.TextButton("Cancelar", on_click=cerrar_dialogo),
            ft.TextButton("Borrar Todo", style=ft.ButtonStyle(bgcolor="#E53935", color="white"), on_click=confirmar_borrado_ventas),
        ],
        actions_alignment=ft.MainAxisAlignment.END
    )

    def abrir_dialogo_confirmacion(e):
        page.dialog = dialogo_confirmacion
        dialogo_confirmacion.open = True
        page.update()

    # --- ASIGNAR MANEJADORES DE EVENTOS A LOS CONTROLES ---
    selected_product.on_change = actualizar_precio

    # --- DISEÑO DE LA INTERFAZ ---
    page.add(
        ft.Container(
            content=ft.Column(
                [
                    ft.Text("KIOSCO DE ACPI", size=32, weight=ft.FontWeight.BOLD, color="#D84315"),
                    ft.Card(elevation=4, content=ft.Container(padding=20, border_radius=10, bgcolor="#FFFAF0", content=ft.Column([
                        ft.Text("Registrar Venta", size=20, weight=ft.FontWeight.BOLD, color="#D84315"),
                        ft.Row([selected_product, cantidad, precio_field], alignment=ft.MainAxisAlignment.CENTER),
                        ft.Row([ft.ElevatedButton("Agregar Venta", on_click=agregar_venta, icon="add_shopping_cart", bgcolor="#4CAF50", color="white")], alignment=ft.MainAxisAlignment.CENTER),
                    ]))),
                    ft.Card(elevation=4, content=ft.Container(padding=20, border_radius=10, bgcolor="#FFF8E1", content=ft.Column([
                        ft.Text("Ventas del Día", size=20, weight=ft.FontWeight.BOLD, color="#FFA000"),
                        ft.Column([tabla], scroll=ft.ScrollMode.ADAPTIVE, height=200),
                        ft.Row([total_label], alignment=ft.MainAxisAlignment.END),
                        ft.Row([
                            ft.ElevatedButton("Borrar Última", on_click=borrar_ultima_venta, icon="delete_sweep", bgcolor="#E91E63", color="white"),
                            ft.ElevatedButton("Borrar Todo", on_click=abrir_dialogo_confirmacion, icon="delete_forever", bgcolor="#B71C1C", color="white"),
                        ], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
                    ]))),
                    ft.Card(elevation=4, content=ft.Container(padding=20, border_radius=10, bgcolor="#F3E5F5", content=ft.Column([
                        ft.Text("Gestionar Productos", size=20, weight=ft.FontWeight.BOLD, color="#6A1B9A"),
                        ft.Text("Agregar Nuevo Producto", size=16),
                        ft.Row([nuevo_producto, nuevo_precio], alignment=ft.MainAxisAlignment.CENTER),
                        ft.Row([ft.ElevatedButton("Guardar Producto", on_click=agregar_producto, icon="save", bgcolor="#7B1FA2", color="white")], alignment=ft.MainAxisAlignment.CENTER),
                        ft.Divider(),
                        ft.Text("Modificar / Eliminar Producto Existente", size=16),
                        ft.Row([producto_modificar, nuevo_precio_modificado], alignment=ft.MainAxisAlignment.CENTER),
                        ft.Row([
                            ft.ElevatedButton("Modificar Precio", on_click=modificar_precio, icon="edit", bgcolor="#FBC02D", color="black"),
                            ft.ElevatedButton("Eliminar Producto", on_click=borrar_producto, icon="delete", bgcolor="#C62828", color="white")
                        ], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
                    ]))),
                ],
                spacing=20,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            ),
            padding=20,
            width=750,
            alignment=ft.alignment.center
        )
    )

    # --- CONFIGURACIÓN INICIAL DEL ESTADO DE LA INTERFAZ ---
    actualizar_tabla()
    actualizar_dropdowns()
    page.update()

# --- INICIAR LA APP ---
if __name__ == "__main__":
    ft.app(target=main)


