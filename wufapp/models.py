from django.db import models
from django.contrib.auth.models import User
import uuid
from django.utils import timezone

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    job = models.CharField(max_length=100, blank=True, null=True)  # Métier
    phone = models.CharField(max_length=15, blank=True, null=True)  # Numéro de téléphone
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)  # Photo de profil
    status = models.CharField(max_length=50, default='offline')  # Statut en ligne
    last_seen = models.DateTimeField(default=timezone.now)

    @property
    def is_online(self):
        return timezone.now() - self.last_seen < timezone.timedelta(seconds=30)



class Chat(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    is_group = models.BooleanField(default=False)
    password  = models.CharField(max_length=255, null=True, blank=True)
    nbre_max_participants = models.IntegerField( null=True, blank=True)
    members = models.ManyToManyField(User, related_name='chats')  # Membres du chat
    active_users = models.ManyToManyField(User, related_name='active_chats', blank=True)  # Utilisateurs actifs dans le chat
    #created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    #created_at = models.DateTimeField( default=timezone.now)
    #category = models.CharField(max_length=20, default='bg-primary')
   
    def __str__(self):
        return self.name
    


class ChatMember(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_admin = models.BooleanField(default=False)
    joined_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('chat', 'user')

class ChatMessage(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='messages1')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages')
    content = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    reply_to = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)  # Réponse à un message

    def __str__(self):
        return f"Message de {self.user.username} à {self.timestamp}"


class ChatFile(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='files1')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(upload_to='chat_files/')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Fichier de {self.user.username} à {self.timestamp}"


class VerificationCode(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='verification_code')
    code = models.CharField(max_length=6, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    def generate_code(self):
        self.code = str(uuid.uuid4().int)[:6]
        self.save()


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.CharField(max_length=255)
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)



class CallSession(models.Model):
    channel_name = models.CharField(max_length=255, unique=True, default=uuid.uuid4)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_calls')
    started_at = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Call {self.channel_name} by {self.creator.username}"
