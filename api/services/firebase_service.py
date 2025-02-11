import firebase_admin
from firebase_admin import credentials, firestore

class FirebaseService:
    def __init__(self, cred_path: str, collection_name: str):
        """
        Inicializa la conexión con Firestore.

        :param cred_path: Ruta al archivo de credenciales de Firebase.
        :param collection_name: Nombre de la colección en Firestore.
        """
        if not firebase_admin._apps:
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)

        self.db = firestore.client()
        self.collection = self.db.collection(collection_name)

    def get_document(self, doc_id: str):
        """
        Obtiene un documento por su ID.

        :param doc_id: ID del documento a obtener.
        :return: Diccionario con los datos del documento o None si no existe.
        """
        doc = self.collection.document(doc_id).get()
        return doc.to_dict() if doc.exists else None

    def get_all_documents(self):
        """
        Obtiene todos los documentos de la colección.

        :return: Lista de diccionarios con los datos de los documentos.
        """
        docs = self.collection.stream()
        return [{**doc.to_dict(), "id": doc.id} for doc in docs]

    def add_document(self, data: dict, doc_id: str = None):
        """
        Agrega un nuevo documento a la colección.

        :param data: Diccionario con los datos del documento.
        :param doc_id: ID opcional del documento. Si no se proporciona, Firestore generará uno automáticamente.
        :return: ID del documento creado.
        """
        if doc_id:
            self.collection.document(doc_id).set(data)
            return doc_id
        else:
            doc_ref = self.collection.add(data)
            return doc_ref[1].id

    def update_document(self, doc_id: str, data: dict):
        """
        Actualiza un documento existente.

        :param doc_id: ID del documento a actualizar.
        :param data: Diccionario con los campos a actualizar.
        """
        self.collection.document(doc_id).update(data)

    def delete_document(self, doc_id: str):
        """
        Elimina un documento por su ID.

        :param doc_id: ID del documento a eliminar.
        """
        self.collection.document(doc_id).delete()
