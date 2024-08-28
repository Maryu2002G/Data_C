from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from bson.objectid import ObjectId

# URI de conexión a MongoDB Atlas (asegúrate de que la contraseña esté correctamente codificada)
uri = "mongodb+srv://maryuesgo2002:mami_prende_la_radi0@cluster0.zgyop.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# Crear un nuevo cliente y conectarse al servidor utilizando ServerApi
client = MongoClient(uri, server_api=ServerApi('1'))

# Enviar un ping para confirmar una conexión exitosa
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(f"Error de conexión: {e}")
    exit(1)

# Conectar a la base de datos
db = client["<dbname>"]  # Reemplaza <dbname> con el nombre de tu base de datos

# Conectar a la colección
collection = db["<collection_name>"]  # Reemplaza <collection_name> con el nombre de tu colección

def create_document():
    """Solicita al usuario los datos para crear un nuevo documento en la colección."""
    nombre = input("Ingrese el nombre: ")
    edad = int(input("Ingrese la edad: "))
    ciudad = input("Ingrese la ciudad: ")
    data = {"nombre": nombre, "edad": edad, "ciudad": ciudad}
    result = collection.insert_one(data)
    print(f"Documento creado con ID: {result.inserted_id}")

def read_documents():
    """Lee y muestra todos los documentos de la colección."""
    documents = collection.find()
    for document in documents:
        print(document)

def update_document():
    """Solicita al usuario el ID del documento y los nuevos datos para actualizar un documento."""
    document_id = input("Ingrese el ID del documento a actualizar: ")
    field = input("Ingrese el campo que desea actualizar (nombre, edad, ciudad): ")
    new_value = input(f"Ingrese el nuevo valor para {field}: ")
    if field == 'edad':  # Convertir a entero si es el campo edad
        new_value = int(new_value)
    result = collection.update_one({"_id": ObjectId(document_id)}, {"$set": {field: new_value}})
    if result.modified_count > 0:
        print(f"Documento con ID {document_id} actualizado correctamente.")
    else:
        print(f"No se encontró el documento con ID {document_id} o no hubo cambios.")

def delete_document():
    """Solicita al usuario el ID del documento para eliminarlo de la colección."""
    document_id = input("Ingrese el ID del documento a eliminar: ")
    result = collection.delete_one({"_id": ObjectId(document_id)})
    if result.deleted_count > 0:
        print(f"Documento con ID {document_id} eliminado correctamente.")
    else:
        print(f"No se encontró el documento con ID {document_id}.")

def menu():
    """Muestra el menú de opciones CRUD y ejecuta la operación seleccionada."""
    while True:
        print("\nMenú de opciones CRUD:")
        print("1. Crear documento")
        print("2. Leer documentos")
        print("3. Actualizar documento")
        print("4. Eliminar documento")
        print("5. Salir")

        opcion = input("Seleccione una opción (1-5): ")

        if opcion == '1':
            create_document()
        elif opcion == '2':
            read_documents()
        elif opcion == '3':
            update_document()
        elif opcion == '4':
            delete_document()
        elif opcion == '5':
            print("Saliendo del programa.")
            break
        else:
            print("Opción no válida. Por favor, seleccione una opción del 1 al 5.")

if __name__ == "__main__":
    menu()
