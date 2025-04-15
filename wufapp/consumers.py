# chat/consumers.py
import json
import base64
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Chat, ChatMessage, ChatFile, Profile, VerificationCode, Notification
from django.core.files.base import ContentFile


class ChatConsumer(AsyncWebsocketConsumer):
    
    async def connect(self):
        self.room_name = "Discussion"
        self.room_group_name = f"chat_{self.room_name}"

        # Récupérer le nom d'utilisateur depuis la query string (ex: ?username=John)
        query_string = self.scope["query_string"].decode()
        username = query_string.split("username=")[-1]
        self.username = username

        # Récupérer les objets utilisateur et chat
        self.user = await sync_to_async(User.objects.get)(username=username)
        self.chat_room = await sync_to_async(Chat.objects.get)(name=self.room_name)

        # Ajouter aux utilisateurs actifs
        await sync_to_async(self.chat_room.active_users.add)(self.user)
        print("Active users: ", self.chat_room.active_users)

        # Joindre le groupe WebSocket
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        # Retirer des utilisateurs actifs
        try:
            await sync_to_async(self.chat_room.active_users.remove)(self.user)
        except Exception:
            pass

        # Quitter le groupe WebSocket
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)


    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        print(text_data_json.get('type'))
        
        if  text_data_json.get('type')=="file" :# in text_data_json:
            file_name = text_data_json["file_name"]
            file_type = text_data_json["file_type"]
            file_content = text_data_json["file_content"]
            username = text_data_json["username"]
            room_name = text_data_json["room_name"]

            # Décoder le contenu base64 du fichier
            decoded_file_content = base64.b64decode(file_content.split(",")[1])
            #print("COntent: ", decoded_file_content)
            # Récupérer ou créer l'utilisateur et la salle de chat
            user, created = await sync_to_async(User.objects.get_or_create)(username=username)
            chat_room, created = await sync_to_async(Chat.objects.get_or_create)(name=room_name)

            # Créer un objet pour le fichier (Stockage dans le modèle)
            chat_file = await sync_to_async(ChatFile.objects.create)(
                user=user,
                chat=chat_room,
                file=ContentFile(decoded_file_content, name=file_name),
               # file_type=file_type
            )

            # Envoyer une notification pour le fichier au groupe
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat.message",
                    "action": "new_file",
                    "file_name": file_name,
                    "file_type": file_type,
                    "username": username,
                    "file_url": chat_file.file.url,  # URL du fichier si nécessaire
                    'messageId': chat_file.id
                })
        
        elif "message" in text_data:
            
            message = text_data_json["message"]
            username = text_data_json["username"]
            room_name = text_data_json["room_name"]
            
            user, created = await sync_to_async(User.objects.get_or_create)(username=username)
            chat_room, created = await sync_to_async(Chat.objects.get_or_create)(name=room_name)
            if message:
                chat_message = await sync_to_async(ChatMessage.objects.create)(
                    user=user,
                    chat=chat_room,
                    content=message
                )

            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name, {"type": "chat.message", 
                                    'action': 'new_message',
                                    "message": message,
                                        "username":username,
                                        'messageId': chat_message.id}
            )

        

    # Receive message from room group
    async def chat_message(self, event):
        """
        Gère la réception et l'envoi des messages ou fichiers au groupe de chat.
        """
        # Vérifie si l'événement contient un fichier ou un message
        action = event.get("action", None)
        
        if action == "new_message":
            # Cas d'un message texte
            message = event.get("message", "")
            username = event.get("username", "anonyme")
            messageId = event.get("messageId")

            
            # Construire un dictionnaire pour le message texte
            content = {
                "type": "text",
                "username": username,
                "message": message,
                "action": "new_message",
                "messageId": messageId
            }
        
        elif action == "new_file":
            # Cas d'un fichier
            file_name = event.get("file_name", "Fichier inconnu")
            file_type = event.get("file_type", "")
            file_url = event.get("file_url", "#")  # URL où le fichier est stocké
            username = event.get("username", "Utilisateur anonyme")
            messageId = event.get("messageId")

            # Construire un dictionnaire pour le fichier
            content = {
                "type": "file",
                "username": username,
                "file_name": file_name,
                "file_type": file_type,
                "file_url": file_url,
                "action": "new_file",
                "messageId": messageId
            }
        else:
            # Action inconnue (par sécurité)
            content = {"error": "Action non reconnue."}
        
        # Envoyer le message (texte ou fichier) au groupe
        await self.send(text_data=json.dumps(content))
