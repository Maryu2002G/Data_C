import mysql.connector
from mysql.connector import Error
from tabulate import tabulate

def conectar():   # esta funcion hace la goneccion al servidor especiamente se conecta a la base de datos employees
    try:
        conexion = mysql.connector.connect(
            host="18.116.82.240",
            port=3306,
            user="studentsucundi",
            password="mami_prende_la_radi0",
            database="employees"                         
        )       
        if conexion.is_connected():
            print("Conexión exitosa")
            return conexion
    except Error as err:
        print(f"Error: {err}")
        return None

def mostrar_tablas(conexion):
    try:
        cursor = conexion.cursor()
        cursor.execute("SHOW TABLES")
        tablas = cursor.fetchall()
        print("Tablas en la base de datos:")
        for tabla in tablas:
            print(tabla[0])
    except Error as err:
        print(f"Error al obtener las tablas: {err}")
    finally:
        cursor.close()
        
def mostrar_estructura_tabla(conexion, nombre_tabla):
    try:
        cursor = conexion.cursor()
        cursor.execute(f"DESCRIBE {nombre_tabla}")
        estructura = cursor.fetchall()
        headers = ["Nombre", "Tipo", "Nulo", "Clave", "Predeterminado", "Extra"]
        # Reorganiza los datos para que coincidan con los encabezados
        filas = [(
            columna[0],  # Nombre
            columna[1],  # Tipo
            columna[2],  # Nulo
            columna[3],  # Clave
            columna[4],  # Predeterminado
            columna[5]   # Extra
        ) for columna in estructura]
        print(f"\nEstructura de la tabla {nombre_tabla}:")
        print(tabulate(filas, headers=headers, tablefmt="grid"))
    except Error as err:
        print(f"Error al obtener la estructura de la tabla {nombre_tabla}: {err}")
    finally:
        cursor.close()
        
def mostrar_datos_tabla(conexion, nombre_tabla):
    try:
        cursor = conexion.cursor()
        cursor.execute(f"SELECT * FROM {nombre_tabla}")
        datos = cursor.fetchall()
        # Obtiene los nombres de las columnas
        cursor.execute(f"DESCRIBE {nombre_tabla}")
        columnas = cursor.fetchall()
        headers = [columna[0] for columna in columnas]
        # Muestra los datos
        print(f"\nDatos de la tabla {nombre_tabla}:")
        print(tabulate(datos, headers=headers, tablefmt="grid"))
    except Error as err:
        print(f"Error al obtener los datos de la tabla {nombre_tabla}: {err}")
    finally:
        cursor.close()
        
def actualizar_datos_tabla(conexion, id_empleado, columna, nuevo_valor):
    try:
        cursor = conexion.cursor()
        if columna == "salario":
            # Convertir nuevo_valor a un número si la columna es salario
            nuevo_valor = float(nuevo_valor)
            query = f"UPDATE empleados SET {columna} = %s WHERE id = %s"
            cursor.execute(query, (nuevo_valor, id_empleado))
        else:
            query = f"UPDATE empleados SET {columna} = %s WHERE id = %s"
            cursor.execute(query, (nuevo_valor, id_empleado))
        
        conexion.commit()
        if cursor.rowcount > 0:
            print(f"Datos actualizados exitosamente. Filas afectadas: {cursor.rowcount}")
        else:
            print("No se encontraron registros para actualizar.")
    except Error as err:
        print(f"Error al actualizar los datos: {err}")
        conexion.rollback()  # Deshace los cambios en caso de error
    finally:
        cursor.close()

if __name__ == "__main__":
    conexion = conectar()
    if conexion:
        try:
            mostrar_tablas(conexion)
            mostrar_estructura_tabla(conexion, "empleados")
            mostrar_datos_tabla(conexion, "empleados")
            
             # Ejemplo de actualización
            id_empleado = 1  # ID del empleado a actualizar
            columna = "salario"  # Columna a actualizar
            nuevo_valor = 56000  # Nuevo valor para la columna
            actualizar_datos_tabla(conexion, id_empleado, columna, nuevo_valor)

            # Mostrar los datos actualizados
            mostrar_datos_tabla(conexion, "empleados")
        finally:
            conexion.close()
            print("Conexión cerrada")

