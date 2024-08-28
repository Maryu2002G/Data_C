import mysql.connector
from mysql.connector import Error
from tabulate import tabulate

def conectar():
    """
    Establece una conexión con la base de datos MySQL usando las credenciales y parámetros proporcionados.
    
    Returns:
        conexion (MySQLConnection): Objeto de conexión a la base de datos si la conexión es exitosa.
        None: Si ocurre un error al intentar conectar.
    """
    try:
        # Establece la conexión a la base de datos
        conexion = mysql.connector.connect(
            host="18.188.124.77",
            port=3306,
            user="studentsucundi",
            password="mami_prende_la_radi0",
            database="employees"                         
        )
        
        # Verifica si la conexión fue exitosa
        if conexion.is_connected():
            print("Conexión exitosa")
            return conexion
    except Error as err:
        # Imprime el error si ocurre
        print(f"Error: {err}")
        return None
    
def mostrar_bases_datos(conexion):
    """
    Muestra todas las bases de datos disponibles en el servidor MySQL.

    Args:
        conexion (MySQLConnection): Objeto de conexión a la base de datos MySQL.
    """
    try:
        cursor = conexion.cursor()
        cursor.execute("SHOW DATABASES")  # Obtiene la lista de bases de datos
        bases_datos = cursor.fetchall()  # Obtiene todas las bases de datos
        
        print("Bases de datos en el servidor:")
        for base_datos in bases_datos:
            print(base_datos[0])  # Imprime el nombre de cada base de datos
    except Error as err:
        # Imprime el error si ocurre
        print(f"Error al obtener las bases de datos: {err}")
    finally:
        cursor.close()  # Cierra el cursor

def mostrar_tablas(conexion):
    """
    Muestra todas las tablas en la base de datos a la que está conectada la variable `conexion`.
    
    Args:
        conexion (MySQLConnection): Objeto de conexión a la base de datos MySQL.
    """
    try:
        cursor = conexion.cursor()
        cursor.execute("SHOW TABLES")  # Obtiene la lista de tablas
        tablas = cursor.fetchall()  # Obtiene todas las tablas
        
        print("Tablas en la base de datos:")
        for tabla in tablas:
            print(tabla[0])  # Imprime el nombre de cada tabla
    except Error as err:
        # Imprime el error si ocurre
        print(f"Error al obtener las tablas: {err}")
    finally:
        cursor.close()  # Cierra el cursor

def mostrar_estructura_tabla(conexion, nombre_tabla):
    """
    Muestra la estructura de una tabla específica, incluyendo nombre, tipo, nulidad, clave, valor predeterminado y extras de cada columna.
    
    Args:
        conexion (MySQLConnection): Objeto de conexión a la base de datos MySQL.
        nombre_tabla (str): Nombre de la tabla cuya estructura se desea mostrar.
    """
    try:
        cursor = conexion.cursor()
        cursor.execute(f"DESCRIBE {nombre_tabla}")  # Obtiene la estructura de la tabla
        estructura = cursor.fetchall()  # Obtiene toda la información de la estructura
        
        # Define los encabezados de la tabla
        headers = ["Nombre", "Tipo", "Nulo", "Clave", "Predeterminado", "Extra"]
        
        # Reorganiza los datos para que coincidan con los encabezados
        filas = [(
            columna[0],  # Nombre de la columna
            columna[1],  # Tipo de la columna
            columna[2],  # Nulo (SI/NO)
            columna[3],  # Clave (PRI/SI)
            columna[4],  # Valor predeterminado
            columna[5]   # Extra (auto_increment, etc.)
        ) for columna in estructura]
        
        print(f"\nEstructura de la tabla {nombre_tabla}:")
        print(tabulate(filas, headers=headers, tablefmt="grid"))  # Muestra los datos en formato de tabla
    except Error as err:
        # Imprime el error si ocurre
        print(f"Error al obtener la estructura de la tabla {nombre_tabla}: {err}")
    finally:
        cursor.close()  # Cierra el cursor

def mostrar_datos_tabla(conexion, nombre_tabla):
    """
    Muestra todos los datos contenidos en una tabla específica. Incluye los nombres de las columnas como encabezados.
    
    Args:
        conexion (MySQLConnection): Objeto de conexión a la base de datos MySQL.
        nombre_tabla (str): Nombre de la tabla cuyos datos se desean mostrar.
    """
    try:
        cursor = conexion.cursor()
        cursor.execute(f"SELECT * FROM {nombre_tabla}")  # Obtiene todos los datos de la tabla
        datos = cursor.fetchall()  # Obtiene todos los datos
        
        # Obtiene los nombres de las columnas
        cursor.execute(f"DESCRIBE {nombre_tabla}")
        columnas = cursor.fetchall()
        headers = [columna[0] for columna in columnas]  # Extrae los nombres de las columnas
        
        print(f"\nDatos de la tabla {nombre_tabla}:")
        print(tabulate(datos, headers=headers, tablefmt="grid"))  # Muestra los datos en formato de tabla
    except Error as err:
        # Imprime el error si ocurre
        print(f"Error al obtener los datos de la tabla {nombre_tabla}: {err}")
    finally:
        cursor.close()  # Cierra el cursor
def actualizar_datos_salaries(conexion, emp_no, from_date, to_date, columna, nuevo_valor):
    """
    Actualiza un campo específico (`columna`) de un registro en la tabla `salaries` según `emp_no`, `from_date`, y `to_date`.

    Args:
        conexion (MySQLConnection): Objeto de conexión a la base de datos MySQL.
        emp_no (int): Número del empleado cuyo registro se actualizará.
        from_date (str): Fecha de inicio del período del registro a actualizar.
        to_date (str): Fecha de fin del período del registro a actualizar.
        columna (str): Nombre de la columna que se actualizará (por ejemplo, `salary`).
        nuevo_valor (int): Nuevo valor para la columna especificada.
    """
    try:
        cursor = conexion.cursor()
        query = f"UPDATE salaries SET {columna} = %s WHERE emp_no = %s AND from_date = %s AND to_date = %s"
        cursor.execute(query, (nuevo_valor, emp_no, from_date, to_date))
        conexion.commit()
        if cursor.rowcount > 0:
            print(f"Datos actualizados exitosamente. Filas afectadas: {cursor.rowcount}")
        else:
            print("No se encontraron registros para actualizar.")
    except Error as err:
        print(f"Error al actualizar los datos: {err}")
        conexion.rollback()
    finally:
        cursor.close()


def eliminar_datos_tabla(conexion, id_empleado):
    """
    Elimina un registro en la tabla `salaries` basado en el `id_empleado` proporcionado.
    
    Args:
        conexion (MySQLConnection): Objeto de conexión a la base de datos MySQL.
        emp_no (int): ID del empleado cuyo registro se eliminará.
    """
    try:
        cursor = conexion.cursor()
        
        # Construye la consulta para eliminar el registro
        query = "DELETE FROM salaries WHERE emp_no = %s"
        cursor.execute(query, (id_empleado,))
        
        conexion.commit()  # Confirma los cambios
        
        if cursor.rowcount > 0:
            print(f"Datos eliminados exitosamente. Filas afectadas: {cursor.rowcount}")
        else:
            print("No se encontraron registros para eliminar.")
    except Error as err:
        # Imprime el error si ocurre y deshace los cambios
        print(f"Error al eliminar los datos: {err}")
        conexion.rollback()
    finally:
        cursor.close()  # Cierra el cursor


def anadir_datos_salaries(conexion, emp_no, salary, from_date, to_date):
    """
    Añade nuevos datos a la tabla `salaries`.

    Args:
        conexion (MySQLConnection): Objeto de conexión a la base de datos MySQL.
        emp_no (int): Número del empleado.
        salary (float): Salario del empleado.
        from_date (str): Fecha de inicio del rango (formato 'YYYY-MM-DD').
        to_date (str): Fecha de fin del rango (formato 'YYYY-MM-DD').
    """
    try:
        cursor = conexion.cursor()
        query = """
        INSERT INTO salaries (emp_no, salary, from_date, to_date) 
        VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query, (emp_no, salary, from_date, to_date))
        conexion.commit()
        print(f"Datos añadidos exitosamente. Número de empleado: {emp_no}")
    except Error as err:
        print(f"Error al añadir los datos: {err}")
        conexion.rollback()
    finally:
        cursor.close()
        
def vaciar_tabla_salaries(conexion):
    """
    Vacía la tabla `salaries` eliminando todos los registros, pero manteniendo la estructura de la tabla.

    Args:
        conexion (MySQLConnection): Objeto de conexión a la base de datos MySQL.
    """
    try:
        cursor = conexion.cursor()
        query = "TRUNCATE TABLE salaries"
        cursor.execute(query)
        conexion.commit()
        print("Tabla `salaries` vaciada exitosamente.")
    except Error as err:
        print(f"Error al vaciar la tabla: {err}")
        conexion.rollback()
    finally:
        cursor.close()


if __name__ == "__main__":
    conexion = conectar()
    if conexion:
        try:
            # Vaciar la tabla `salaries`
            #vaciar_tabla_salaries(conexion)
            mostrar_tablas(conexion)
            mostrar_estructura_tabla(conexion, "salaries")
            mostrar_datos_tabla(conexion, "salaries")

            # Ejemplo de actualización
            id_empleado = 2  # ID del salaro a actualizar
            columna = "to_date"  # Columna a actualizar
            nuevo_valor = "2024-12-31"  # Nuevo valor para la columna
            actualizar_datos_tabla(conexion, id_empleado, columna, nuevo_valor)

            # Ejemplo de eliminación
            emp_no_eliminar = 2  # Número del empleado
            eliminar_datos_tabla(conexion, emp_no_eliminar)

            # Ejemplo de adición
            emp_no_nuevo = 2  # Número del nuevo empleado
            salario_nuevo = 56000  # Salario del nuevo empleado
            anadir_datos_salaries(conexion, emp_no_nuevo, salario_nuevo, '2024-01-01', '2024-12-31')

            # Mostrar los datos actualizados
            mostrar_datos_tabla(conexion, "salaries")
        finally:
            conexion.close()
            print("Conexión cerrada")
