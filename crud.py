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

def actualizar_datos_tabla(conexion, id_empleado, columna, nuevo_valor):
    """
    Actualiza un campo específico (`columna`) de un registro en la tabla `empleados` según el `id_empleado` proporcionado.
    
    Args:
        conexion (MySQLConnection): Objeto de conexión a la base de datos MySQL.
        id_empleado (int): ID del empleado cuyo registro se actualizará.
        columna (str): Nombre de la columna que se actualizará (por ejemplo, `salario`, `puesto`).
        nuevo_valor (str/float): Nuevo valor para la columna especificada. Si la columna es `salario`, debe ser un número.
    """
    try:
        cursor = conexion.cursor()
        
        # Si la columna es 'salario', convierte el nuevo valor a float
        if columna == "salario":
            nuevo_valor = float(nuevo_valor)
        
        # Construye la consulta para actualizar el registro
        query = f"UPDATE empleados SET {columna} = %s WHERE id = %s"
        cursor.execute(query, (nuevo_valor, id_empleado))
        
        conexion.commit()  # Confirma los cambios
        
        if cursor.rowcount > 0:
            print(f"Datos actualizados exitosamente. Filas afectadas: {cursor.rowcount}")
        else:
            print("No se encontraron registros para actualizar.")
    except Error as err:
        # Imprime el error si ocurre y deshace los cambios
        print(f"Error al actualizar los datos: {err}")
        conexion.rollback()
    finally:
        cursor.close()  # Cierra el cursor

def eliminar_datos_tabla(conexion, id_empleado):
    """
    Elimina un registro en la tabla `empleados` basado en el `id_empleado` proporcionado.
    
    Args:
        conexion (MySQLConnection): Objeto de conexión a la base de datos MySQL.
        id_empleado (int): ID del empleado cuyo registro se eliminará.
    """
    try:
        cursor = conexion.cursor()
        
        # Construye la consulta para eliminar el registro
        query = "DELETE FROM empleados WHERE id = %s"
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

def anadir_datos_tabla(conexion, id_empleado, nombre, puesto, salario):
    """
    Añade un nuevo registro a la tabla `empleados` con los valores proporcionados para `id_empleado`, `nombre`, `puesto` y `salario`.
    
    Args:
        conexion (MySQLConnection): Objeto de conexión a la base de datos MySQL.
        id_empleado (int): ID del nuevo empleado.
        nombre (str): Nombre del nuevo empleado.
        puesto (str): Puesto del nuevo empleado.
        salario (float): Salario del nuevo empleado.
    """
    try:
        cursor = conexion.cursor()
        
        # Construye la consulta para insertar un nuevo registro
        query = """
        INSERT INTO empleados (id, nombre, puesto, salario) 
        VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query, (id_empleado, nombre, puesto, salario))
        
        conexion.commit()  # Confirma los cambios
        
        print(f"Datos añadidos exitosamente. ID del empleado: {id_empleado}")
    except Error as err:
        # Imprime el error si ocurre y deshace los cambios
        print(f"Error al añadir los datos: {err}")
        conexion.rollback()
    finally:
        cursor.close()  # Cierra el cursor

if __name__ == "__main__":
    conexion = conectar()
    if conexion:
        try:
            mostrar_bases_datos(conexion)  # Muestra todas las bases de datos en el servidor
            mostrar_tablas(conexion)
            mostrar_estructura_tabla(conexion, "empleados")
            mostrar_datos_tabla(conexion, "empleados")
            
            # Ejemplo de actualización
            id_empleado = 6  # ID del empleado a actualizar
            columna_empleados = "salario"  # Columna a actualizar
            nuevo_valor_empleados = 50000  # Nuevo valor para la columna
            //actualizar_datos_empleados(conexion, id_empleado, columna_empleados, nuevo_valor_empleados)

            # Ejemplo de eliminación
            id_empleado_eliminar = 1  # ID del empleado a eliminar
            eliminar_datos_tabla(conexion, id_empleado_eliminar)

            # Ejemplo de adición
            id_empleado_nuevo = 2  # Nuevo ID del empleado
            nombre_nuevo = "Cristian"  # Nombre del nuevo empleado
            puesto = "Concerje"       # Puesto del nuevo empleado
            salario_nuevo = 45000     # Salario del nuevo empleado
            anadir_datos_tabla(conexion, id_empleado_nuevo, nombre_nuevo, puesto, salario_nuevo)

            # Mostrar los datos actualizados
            mostrar_datos_tabla(conexion, "empleados")
        finally:
            conexion.close()
            print("Conexión cerrada")
