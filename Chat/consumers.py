import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Extraer parámetros y usuario
        self.solicitud_id = self.scope['url_route']['kwargs']['chat_id']
        self.user = self.scope['user']

        # Validar usuario
        if self.user.is_anonymous or self.user.tipo_usuario not in ["Aspirante", "RRHH"]:
            await self.accept()
            await self.send(text_data=json.dumps({'error': 'Usuario no autorizado.'}))
            await self.close()
            return

        # Obtener chat y miembro
        try:
            self.chat = await self.get_chat()
            self.member = await self.get_member()
        except Exception as e:
            await self.accept()
            await self.send(text_data=json.dumps({'error': str(e)}))
            await self.close()
            return

        # Unirse al grupo y aceptar
        self.room_group_name = f"chat_{self.chat.id}"
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        # Enviar historial solo si hay mensajes
        try:
            history = await self.get_history()
            if history:
                for msg in history:
                    await self.send(text_data=json.dumps({
                        'message': msg.contenido,
                        'sender': msg.userid.userid.username,
                        'timestamp': msg.timestamp.isoformat(),
                        'history': True
                    }))
        except Exception as e:
            await self.send(text_data=json.dumps({'error': 'Error cargando historial: ' + str(e)}))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message = data.get('message', '').strip()
            if not message:
                return

            # Crear y redistribuir mensaje
            chat_msg = await self.create_message(message)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': chat_msg.contenido,
                    'sender': self.user.username,
                    'timestamp': chat_msg.timestamp.isoformat(),
                    'history': False
                }
            )
        except Exception as e:
            await self.send(text_data=json.dumps({'error': 'Error interno: ' + str(e)}))
            await self.close()

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender': event['sender'],
            'timestamp': event['timestamp'],
            'history': event.get('history', False)
        }))

    @database_sync_to_async
    def get_chat(self):
        from Chat import models as Chat_models
        return Chat_models.Chat.objects.get(solicitud_id=self.solicitud_id)

    @database_sync_to_async
    def get_member(self):
        from Chat import models as Chat_models
        return Chat_models.Miembro_Chat.objects.get(chat_id=self.chat, userid=self.user)

    @database_sync_to_async
    def get_history(self):
        from Chat import models as Chat_models
        return list(
            Chat_models.Mensaje.objects.filter(chat_id=self.chat)
            .select_related('userid__userid')
            .order_by('timestamp')
        )

    @database_sync_to_async
    def create_message(self, message_text):
        from Chat import models as Chat_models
        return Chat_models.Mensaje.objects.create(
            contenido=message_text,
            chat_id=self.chat,
            userid=self.member
        )
