
from django.shortcuts import render, redirect, get_object_or_404

from django.http import JsonResponse, HttpResponseForbidden
from .models import *

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

from django.db.models import Q
from django.core.mail import EmailMessage
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.core.validators import validate_email
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.exceptions import ValidationError
import codecs, math
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib, ssl




email_address = settings.EMAIL_HOST_USER
email_password = settings.EMAIL_HOST_PASSWORD

smtp_address = settings.EMAIL_HOST
smtp_port = 465


@login_required
def home(request):
    chat = get_object_or_404(Chat, name="Discussion")
    if not chat.members.filter(id=request.user.id).exists():
       chat.members.add(request.user)

    indentifiant = str(request.user.username)[:2]
    list_users = User.objects.all()
    active_calls = CallSession.objects.filter(is_active=True)

    return render(request, "home.html", {'list_users': list_users, 'active_calls': active_calls, 'indentifiant': indentifiant})

@login_required
def online_users(request):
    time_threshold = timezone.now() - timezone.timedelta(seconds=30)
    online_profiles = Profile.objects.filter(last_seen__gte=time_threshold)
    data = {
        "online_users": [profile.user.username for profile in online_profiles]
    }
    return JsonResponse(data)

def register(request):
    mess = ""
    if request.method == "POST":
        
        print("="*5, "NEW REGISTRATION", "="*5)
        
        prenom= request.POST.get("firstname", None)
        nom= request.POST.get("lastname", None)
        username = ''.join(f"{nom}{prenom}".split())
        email = request.POST.get("email", None)
        pass1 = request.POST.get("password1", None)
        pass2 = request.POST.get("password2", None)
        phone = request.POST.get("phone", None)  # Récupérez le champ "Numéro de téléphone"
        job = request.POST.get("job", None)  # Récupérez le champ "Numéro de téléphone"
        print(username, email, pass1, pass2)
        try:
            validate_email(email)
        except:
            mess = "Invalid Email"
        if pass1 != pass2 :
            mess += " Password not match"
        if User.objects.filter(Q(email= email)| Q(username=username)).first():
            mess += f" Exist user with email {email} or username {username}"
        print("Message: ", mess)
        if mess=="":
            try:
                    validate_password(pass1)
                    user = User(username= username, email = email, first_name=prenom, last_name=nom)
                    user.save()
                    user.password = pass1
                    user.set_password(user.password)
                    user.save()
                    
                    profile = Profile.objects.create(user = user, job= job, phone=phone)
                    profile.save()
                    subject = "Bienvenue sur Wufa !"

                    email_message = f"""
                    <!DOCTYPE html>
                    <html lang="fr">
                    <head>
                        <meta charset="UTF-8">
                        <meta name="viewport" content="width=device-width, initial-scale=1.0">
                        <title>Bienvenue sur Wufa !</title>
                        <style>
                            body {{
                                font-family: Arial, sans-serif;
                                background-color: #f4f7fa;
                                color: #333;
                                margin: 0;
                                padding: 0;
                            }}
                            .container {{
                                max-width: 600px;
                                margin: 20px auto;
                                padding: 20px;
                                background-color: #ffffff;
                                border-radius: 8px;
                                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                            }}
                            h1 {{
                                color: #d9534f;
                                text-align: center;
                            }}
                            p {{
                                font-size: 16px;
                                line-height: 1.6;
                                margin: 10px 0;
                            }}
                            ul {{
                                font-size: 16px;
                                margin: 10px 0;
                            }}
                            li {{
                                margin-bottom: 8px;
                            }}
                            .highlight {{
                                font-weight: bold;
                                color: #d9534f;
                            }}
                            .footer {{
                                text-align: center;
                                font-size: 14px;
                                margin-top: 20px;
                                color: #888;
                            }}
                            .button {{
                                display: inline-block;
                                padding: 12px 20px;
                                margin-top: 20px;
                                background-color: #d9534f;
                                color: #fff;
                                text-decoration: none;
                                border-radius: 4px;
                                text-align: center;
                            }}
                            .button:hover {{
                                background-color: #c9302c;
                            }}
                        </style>
                    </head>
                    <body>
                        <div class="container">
                            <h1>Bienvenue sur Wufa, {prenom} ! 👩‍🍳👨‍🍳</h1>
                            <p>Bonjour {prenom},</p>
                            <p>Bienvenue sur <span class="highlight">Wufa</span>, la plateforme innovante qui vous accompagne dans votre apprentissage culinaire ! Nous sommes ravis de vous avoir parmi nous et convaincus que cette aventure sera aussi savoureuse qu’enrichissante.</p>
                            <p><span class="highlight">Wufa</span> utilise une technologie avancée, le modèle RAG (Retrieval-Augmented Generation), pour vous proposer des quiz personnalisés à partir des cours publiés par vos professeurs. Cela vous permet de tester vos connaissances de manière interactive et dynamique, tout en renforçant les compétences acquises dans chaque leçon.</p>
                            <p><strong>Voici ce que vous pouvez attendre de Wufa :</strong></p>
                            <ul>
                                <li><span class="highlight">Des quiz adaptés à vos cours :</span> Chaque question générée est directement liée au contenu de vos leçons, garantissant une révision ciblée et efficace.</li>
                                <li><span class="highlight">Une progression suivie en temps réel :</span> Vous pourrez suivre votre performance et identifier les sujets à approfondir pour progresser.</li>
                                <li><span class="highlight">Une expérience d’apprentissage flexible :</span> Les quiz sont accessibles à tout moment, pour vous permettre d’apprendre à votre rythme et selon vos disponibilités.</li>
                            </ul>
                            <p>Pour commencer, explorez vos cours disponibles sur votre tableau de bord, et laissez-vous guider par les quiz adaptés à chaque leçon. Plus vous interagissez avec le contenu, plus vous renforcez vos compétences culinaires !</p>
                            <p>Si vous avez des questions ou besoin d’aide, n’hésitez pas à nous contacter. Notre équipe est là pour vous accompagner à chaque étape de votre apprentissage.</p>
                            <p>Bon apprentissage et à très bientôt sur <span class="highlight">Wufa</span> !</p>
                            <div class="footer">
                                <p>Cordialement,</p>
                                <p>L’équipe Wufa</p>
                                <p>03 27 51 77 47</p>
                                <p><a href="https://Wufa.de" target="_blank">https://Wufa.de</a></p>
                            </div>
                        </div>
                    </body>
                    </html>
                    """

                    #emailsender(subject, email_message, email_address,  user.email)

                    mess = f"Welcome, {prenom}! Your account has been successfully created. To activate your account, please retrieve your verification code from the email sent to {user.email}"
                        
                    messages.info(request, mess)

                    verification_code, created = VerificationCode.objects.get_or_create(user=user)
                    verification_code.generate_code()
                    print(verification_code.code)
                    
                    subject = "Votre code de vérification Wufa"

                    email_message = f"""
                    <!DOCTYPE html>
                    <html lang="fr">
                    <head>
                        <meta charset="UTF-8">
                        <meta name="viewport" content="width=device-width, initial-scale=1.0">
                        <title>Code de vérification</title>
                        <style>
                            body {{
                                font-family: Arial, sans-serif;
                                background-color: #f4f7fa;
                                color: #333;
                                margin: 0;
                                padding: 0;
                            }}
                            .container {{
                                max-width: 600px;
                                margin: 20px auto;
                                padding: 20px;
                                background-color: #ffffff;
                                border-radius: 8px;
                                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                            }}
                            h1 {{
                                color: #d9534f;
                                text-align: center;
                            }}
                            p {{
                                font-size: 16px;
                                line-height: 1.6;
                                margin: 10px 0;
                            }}
                            .code-box {{
                                text-align: center;
                                margin: 20px 0;
                            }}
                            .code {{
                                display: inline-block;
                                font-size: 24px;
                                font-weight: bold;
                                background-color: #f8f9fa;
                                padding: 10px 20px;
                                border: 1px solid #ddd;
                                border-radius: 5px;
                                color: #d9534f;
                                letter-spacing: 2px;
                            }}
                            .footer {{
                                text-align: center;
                                font-size: 14px;
                                margin-top: 20px;
                                color: #888;
                            }}
                        </style>
                    </head>
                    <body>
                        <div class="container">
                            <h1>Votre code de vérification</h1>
                            <p>Bonjour {prenom},</p>
                            <p>Voici votre code de vérification pour accéder à votre compte Wufa. Entrez ce code sur notre site pour compléter votre connexion ou validation :</p>
                            <div class="code-box">
                                <span class="code">{verification_code.code}</span>
                            </div>
                            <p>Ce code est valide pendant les <strong>30 prochaines minutes</strong>. Si vous n’avez pas demandé ce code, veuillez ignorer cet e-mail ou nous contacter immédiatement.</p>
                            <div class="footer">
                                <p>Merci de faire confiance à <strong>Wufa</strong> !</p>
                                <p>03 27 51 77 47 | <a href="https://Wufa.de" target="_blank">https://Wufa.de</a></p>
                            </div>
                        </div>
                    </body>
                    </html>
                    """

                    #emailsender(subject, email_message, email_address, user.email)
                                    
                    return redirect("code")
            except Exception as e:
                    print("error: ", type(e), e)
                    #err = " ".join(e)
                    
                    messages.error(request, f"Erreur survenue lors de la creation de compte, veuillez reessayer.")
                    return render(request, template_name="register.html")
            
        else:
            messages.info(request, mess)

    return render(request, template_name="register.html")


@login_required
def get_chat_users(request):
    chat_room = get_object_or_404(Chat, name="Discussion")
    all_users = chat_room.members.all()
    active_users = chat_room.active_users.all()
    
    data = {
        "users": [
            {
                "username": user.username,
                "is_active": user in active_users
            }
            for user in all_users
        ]
    }
    print('Active users: ', [user for user in active_users])
    print('Active users: ', [user for user in all_users])
    return JsonResponse(data)


@login_required
def chat_view(request):
    return render(request, "chat/chat_room.html", {
        "username": request.user.username
    })



def connection(request):
    mess = ""

    '''if request.user.is_authenticated:
         return redirect("dashboard")'''
    if request.method == "POST":
        
        print("="*5, "NEW CONECTION", "="*5)
        email = request.POST.get("email")
        password = request.POST.get("password")
        
        try:
            validate_email(email)
        except:
            mess = "Invalid Email !!!"
        #authen = User.lo
        if mess=="":
            user = User.objects.filter(email= email).first()
            if user:
                auth_user= authenticate(username= user.username, password= password)
                if auth_user:
                    print("Utilisateur infos: ", auth_user.username, auth_user.email)
                    login(request, auth_user)
                    
                    return redirect("home")
                else :
                    mess = "Incorrect password"
            else:
                mess = "user does not exist"
            
        messages.info(request, mess)

    return render(request, template_name="login.html")




from django.core.mail import send_mail  # Use Django's email sending
from django.utils.html import strip_tags # For plain text version
from django.template.loader import render_to_string # For cleaner HTML

def forgotpassword(request):
    if request.method == "POST":
        email = request.POST.get("email")
        user = User.objects.filter(email=email).first()

        if user:
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.id))
            current_site = request.META["HTTP_HOST"] # Replace with your actual domain
            subject = "Password Reset Wufa"

            # Use a template for cleaner HTML
            html_message = render_to_string('account/password_reset_email.html', {
                'user': user,
                'reset_link': f"{current_site}/updatepassword/{token}/{uid}/",
            })

            plain_message = strip_tags(html_message) # Create plain text version

            send_mail(
                subject,
                plain_message,  # Send plain text version
                email_address,  # From email
                [user.email],  # To email(s)
                html_message=html_message,  # Send HTML version
            )

            messages.success(request, f"A reset password email has been sent to {user.email}.")
        else:
            messages.success(request, "The email address does not match any account.")

    return render(request, "account/forgot_password.html")

def updatepassword(request, token, uid):
    print(request.user.username, token, uid)
    try:
            user_id = urlsafe_base64_decode(uid)
            decode_uid = codecs.decode(user_id, "utf-8")
            user = User.objects.get(id= decode_uid)
                         
    except:
            return HttpResponseForbidden("You are not authorize to edit this page")
    print("Utilisateur: ", user)
    checktoken = default_token_generator.check_token( user, token)
    if not checktoken:
        return HttpResponseForbidden("You are not authorize to edit this page, your token is not valid or have expired")
    if request.method =="POST":
            user = User.objects.get(id= decode_uid)
            pass1= request.POST.get('pass1')
            pass2= request.POST.get('pass2')
            if pass1 == pass2:
                 try:
                        validate_password(pass1)
                        user.password = pass1
                        user.set_password(user.password)
                        user.save()
                        messages.success(request, "Your password is update sucessfully")
                 except ValidationError as e:
                      messages.error(request, str(e))
                      
                       
                 return redirect('login')
            else:
                 messages.eror(request, "Passwords not match")
        
    return render(request, "account/update_password.html")

def code(request):
    mess = ""

    if request.method == "POST":
        print("=" * 5, "NEW CONNECTION_code", "=" * 5)

        email = request.POST.get("email")
        code_v = request.POST.get("code")
        
        # Vérifier si l'email est fourni et s'il existe dans la base de données
        if not email:
            mess = "L'email est requis."
            messages.error(request, mess)
            return render(request, "code.html")
        
        user = User.objects.filter(email=email).first()
        
        # Si l'utilisateur n'existe pas
        if not user:
            mess = "Aucun utilisateur trouvé avec cet email."
            messages.error(request, mess)
            return render(request, "code.html")

        try:
            print("1hjjk")
            # Récupérer ou créer le code de vérification pour l'utilisateur
            verification_code, created = VerificationCode.objects.get_or_create(user=user)
            
            print("code: ", verification_code.code)

            # Vérification du code
            if str(code_v) == str(verification_code.code):
                messages.success(request, "Votre compte est activé. Connectez-vous!")

               
                # Redirection vers la page de connexion
                return redirect("login")

            else:
                # Code incorrect
                mess = "Code de vérification invalide."
                messages.info(request, mess)

        except Exception as e:
            # Gérer les erreurs dans le bloc try, par exemple, si la création du code échoue
            print("Erreur lors de la récupération du code:", str(e))
            mess = "Une erreur est survenue. Veuillez vérifier l'email et/ou le code."
            messages.error(request, mess)

    return render(request, template_name="code.html" )

def deconnexion(request):
         print("Deconnexion")
         logout(request)
         return redirect("login")
    
@login_required
def contact(request):
    context={}
    if request.method =="POST":
        
            Subject = request.POST.get("subject")

            Gmail = request.POST.get("email")
            message = f"Nom d'utilisateur: {request.user.username} " f'Adresse mail: {Gmail}\n' + request.POST.get("message")
            print(message)
            
            print(Gmail,  [settings.EMAIL_HOST_USER])
            emailsender(Subject, message, settings.EMAIL_HOST_USER, settings.EMAIL_HOST_USER, contact="yes")
            

            messages.success(request, "Nous avons bien reçu votre message. Nous vous revenons très bientot !!!")
           

            #return JsonResponse({'success': True, 'mess': "Your message is succesfull send  !!!"})
            return redirect("home")
        #return HttpResponseRedirect("y")
        #return HttpResponse("yours message is succesfull send")
    return redirect("home")

def parametres(request):
     return render(request, "home.html")


def edit_profile(request):
     return render(request, "home.html")


def emailsender(Subject, html, email_address,  user_email, contact = None):
    message = MIMEMultipart("alternative")
    # on ajoute un sujet
    message["Subject"] = Subject
    # un émetteur
    message["From"] = f"Wufa <{email_address}>"
    # un destinataire
    message["To"] = user_email
    # on crée deux éléments MIMEText 
    html_mime = MIMEText(html, 'html')
    if contact:
        user_email = [user_email, "sitsopekokou@gmail.com"]
    # on attache ces deux éléments 
    message.attach(html_mime)

    # on crée la connexion
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_address, smtp_port, context=context) as server:
        # connexion au compte
        server.login(email_address, email_password)
        # envoi du mail
        server.sendmail(email_address, user_email, message.as_string())



import datetime
import hmac
import hashlib
import time
from django.conf import settings
from django.http import JsonResponse

def generate_agora_token(request, channel_name):
    # Paramètres nécessaires
    app_id = settings.AGORA_APP_ID  # Ton App ID Agora
    app_certificate = settings.AGORA_APP_CERTIFICATE  # Ton App Certificate Agora
    uid = 0  # UID unique de l'utilisateur (0 pour un client aléatoire)
    role = 1  # 1 = Publisher (l'utilisateur rejoint le canal)
    expire_time = 3600  # Le token expire après 1 heure

    # Générer le timestamp d'expiration
    current_time = int(time.time())
    expire_timestamp = current_time + expire_time

    # Créer la chaîne de signature
    sig_str = f"{app_id}{expire_timestamp}{channel_name}{uid}"

    # Créer la signature en utilisant HMAC et SHA1
    signature = hmac.new(
        app_certificate.encode('utf-8'),
        sig_str.encode('utf-8'),
        hashlib.sha1
    ).hexdigest()

    # Créer le token
    token = f"1.{expire_timestamp}.{signature}"
    print("Token: ", token)
    # Retourner le token sous forme de réponse JSON
    return JsonResponse({'token': token})






from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import CallSession
from django.conf import settings
import random
import time
import json
from agora_token_builder import RtcTokenBuilder



@login_required
def index(request):
    indentifiant = str(request.user.username)[:2]
    chats = Chat.objects.all()
    return render(request, 'index.html', {
        'username': request.user.username,
        'indentifiant': indentifiant, 
        'chats': chats, 
    })



from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from .models import Chat, ChatMember

@login_required
@csrf_exempt
def create_chat(request):
    if request.method == 'POST':
        try:
            # Récupérer les données du formulaire
            name = request.POST.get('name')
            description = request.POST.get('description')
            #category = request.POST.get('category')
            max_participants = int(request.POST.get('max_participants', 20))
            password = request.POST.get('password', '')
            
            # Validation
            if not name or not description:
                return JsonResponse({'success': False, 'error': 'Titre et description requis'})
            
            if max_participants < 2:
                return JsonResponse({'success': False, 'error': 'Au moins 2 participants sont requis'})
            
            # Créer le chat
            chat = Chat.objects.create(
                name=name,
                description=description,
                #category=category,
                #max_participants=max_participants,
                password=password,
                #created_by=request.user
            )
            
            # Ajouter le créateur comme membre
            ChatMember.objects.create(
                chat=chat,
                user=request.user,
                is_admin=True
            )
            
            return JsonResponse({
                'success': True, 
                'chat_id': chat.id,
                'message': 'Discussion créée avec succès!'
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Méthode non autorisée'})


def edit_profile(request):
     return render(request, "index.html")

@login_required
def create_call(request):
    channel_name = f"call-{int(time.time())}-{random.randint(0, 10000)}"
    call_session = CallSession.objects.create(
        channel_name=channel_name,
        creator=request.user
    )
    return redirect('call_room', channel_name=channel_name)

def call_room(request, channel_name):
    call_session = get_object_or_404(CallSession, channel_name=channel_name, is_active=True)
    
    # Générer un UID aléatoire pour l'utilisateur
    uid = random.randint(1, 230)
    
    context = {
        'app_id': settings.AGORA_APP_ID,
        'channel_name': channel_name,
        'uid': uid
    }
    return render(request, 'call.html', context)

def generate_token(request):
    app_id = settings.AGORA_APP_ID
    app_certificate = settings.AGORA_APP_CERTIFICATE
    channel_name = request.GET.get('channel')
    uid = request.GET.get('uid')
    
    if not channel_name or not uid:
        return JsonResponse({'error': 'Channel name and UID are required'}, status=400)
    
    # Générer un token qui expire après 24 heures
    expiration_time_in_seconds = 24 * 3600
    current_timestamp = int(time.time())
    privilege_expired_ts = current_timestamp + expiration_time_in_seconds
    
    token = RtcTokenBuilder.buildTokenWithUid(
        app_id, app_certificate, channel_name, int(uid), 
        RtcTokenBuilder.Role_Publisher, privilege_expired_ts
    )
    
    return JsonResponse({'token': token})