import os
import datetime

from django.conf import settings
from django.shortcuts import render, HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.template.loader import get_template

from xhtml2pdf import pisa
from xhtml2pdf.files import pisaFileObject

from .models import ChatMessage
from .services import ChatService


# --- SOHBET EKRANI ---

@login_required
def chat_room(request):
    messages = ChatMessage.objects.filter(user=request.user).order_by('created_at')
    return render(request, 'chat/room.html', {'chat_messages': messages})


# --- MESAJ GÖNDER ---

@login_required
@require_http_methods(["POST"])
def send_message(request):
    user_message = request.POST.get('message', '').strip()
    image_file = request.FILES.get('image')

    if not user_message and not image_file:
        return HttpResponse("")

    # Kullanıcı mesajını kaydet
    ChatMessage.objects.create(
        user=request.user,
        sender_type='client',
        message=user_message,
        image=image_file,
        is_read=True
    )

    if image_file:
        image_file.seek(0)

    # AI cevabı üret
    service = ChatService()
    ai_response_text = service.generate_response(request.user, user_message, image_file)

    ai_msg = ChatMessage.objects.create(
        user=request.user,
        sender_type='ai',
        message=ai_response_text,
        is_read=True
    )

    return render(request, 'chat/partials/message_bubble.html', {'msg': ai_msg})


# --- GEÇMİŞİ TEMİZLE ---

@login_required
@require_http_methods(["POST"])
def clear_history(request):
    ChatMessage.objects.filter(user=request.user).delete()
    return render(request, 'chat/partials/empty_state_content.html')


# --- xhtml2pdf İÇİN DOSYA ÇÖZÜMLEME (MEDYA & STATİK) ---

def link_callback(uri, rel):
    """
    xhtml2pdf'in <img src="..."> ve @font-face src: url(...) gibi
    linklerini gerçek dosya yoluna çevirir.
    Sadece MEDIA ve STATIC için kullanıyoruz.
    """
    path = None

    # MEDIA dosyaları
    if uri.startswith(settings.MEDIA_URL):
        path = os.path.join(settings.MEDIA_ROOT, uri.replace(settings.MEDIA_URL, ""))

    # STATIC dosyaları
    elif uri.startswith(settings.STATIC_URL):
        static_root = os.path.join(settings.BASE_DIR, 'static')
        path = os.path.join(static_root, uri.replace(settings.STATIC_URL, "").lstrip('/'))

    if path and not os.path.isfile(path):
        return None

    return path


# --- SOHBET GEÇMİŞİNİ PDF OLARAK İNDİR ---

@login_required
def download_history(request):
    messages = ChatMessage.objects.filter(user=request.user).order_by('created_at')

    # Windows + xhtml2pdf temp TTF bug'ı için patch
    # (NamedTemporaryFile kullanıp sonra ReportLab tarafında TTFError vermesini engellemek için)
    pisaFileObject.getNamedFile = lambda self: self.uri

    context = {
        'messages': messages,
        'user': request.user,
        'date': datetime.datetime.now(),
    }

    template = get_template('chat/history_pdf.html')
    html = template.render(context)

    response = HttpResponse(content_type='application/pdf')
    filename = f"DietMaster_Gecmis_{datetime.date.today()}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    pisa_status = pisa.CreatePDF(
        html,
        dest=response,
        encoding='utf-8',
        link_callback=link_callback,
    )

    if pisa_status.err:
        return HttpResponse('PDF oluşturulurken hata meydana geldi.', status=500)

    return response
