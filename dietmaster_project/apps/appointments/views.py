from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils.dateparse import parse_date
from datetime import datetime, date
import json
from .models import Appointment
from .utils import CalendarUtils

@login_required
def calendar_view(request):
    # Yıl ve Ay parametrelerini al, yoksa şu anki zamanı kullan
    year = int(request.GET.get('year', datetime.now().year))
    month = int(request.GET.get('month', datetime.now().month))
    
    cal_utils = CalendarUtils(year, month)
    month_days = cal_utils.get_month_days()
    
    # Ay isimleri için
    month_name = date(year, month, 1).strftime('%B')
    
    # BUGFIX: O ayki randevuları çek - SADECE AKTİF OLANLAR (iptal/red edilenler takvimde görünmemeli)
    # Cancelled appointments should not block calendar display for any user
    if request.user.role == 'ADMIN':
        appointments = Appointment.objects.active().filter(
            date__year=year, 
            date__month=month
        ).select_related('client')
    else:
        appointments = Appointment.objects.active().filter(
            client=request.user,
            date__year=year, 
            date__month=month
        )
    
    # Randevuları günlere göre grupla: { date_obj: [app1, app2], ... }
    appointments_by_date = {}
    for app in appointments:
        if app.date not in appointments_by_date:
            appointments_by_date[app.date] = []
        appointments_by_date[app.date].append(app)

    context = {
        'month_days': month_days,
        'year': year,
        'month': month,
        'month_name': month_name,
        'appointments_by_date': appointments_by_date,
        'today': datetime.now().date(),
    }
    
    return render(request, 'appointments/calendar.html', context)

@login_required
def get_slots_view(request):
    date_str = request.GET.get('date')
    if not date_str:
        return HttpResponse('<div class="text-center text-danger py-5">Tarih parametresi eksik.</div>')
        
    selected_date = parse_date(date_str)
    if not selected_date:
        return HttpResponse('<div class="text-center text-danger py-5">Geçersiz tarih formatı.</div>')

    # BUGFIX: Always fetch fresh slot data - prevent stale cached slot information
    try:
        slots = CalendarUtils.get_available_slots(selected_date)
    except Exception as e:
        # Hata durumunda kullanıcıya bilgi ver
        return HttpResponse(f'<div class="text-center text-danger py-5"><i class="bi bi-exclamation-triangle fs-1 mb-3"></i><p>Saatler yüklenirken bir hata oluştu.</p></div>')
    
    # Çalışma günü kontrolü (Mesaj göstermek için)
    from .models import DietitianAvailability
    is_working_day = True
    # Eğer sistemde availability tanımı varsa ve bugün için kayıt yoksa -> Çalışma günü değil
    if DietitianAvailability.objects.exists() and not DietitianAvailability.objects.filter(weekday=selected_date.weekday()).exists():
        is_working_day = False
    
    # Eğer Admin ise o günkü randevuları da gösterelim
    day_appointments = []
    if request.user.role == 'ADMIN':
        # BUGFIX: Sadece aktif randevuları göster (iptal/red edilenleri gizle)
        # Using .active() manager method for consistency
        day_appointments = Appointment.objects.active().for_date(selected_date).select_related('client').order_by('time')
    
    # BUGFIX: Calculate available slots count in Python (Django templates don't have selectattr)
    available_slots_count = len([s for s in slots if s['available']])
    has_available_slots = available_slots_count > 0
    
    context = {
        'slots': slots,
        'selected_date': selected_date,
        'day_appointments': day_appointments,
        'is_working_day': is_working_day,
        'available_slots_count': available_slots_count,
        'has_available_slots': has_available_slots,
    }
    
    # BUGFIX: Add no-cache headers to prevent browser/HTMX from serving stale slot data
    response = render(request, 'appointments/partials/slots_modal_content.html', context)
    response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response

@login_required
def create_appointment(request):
    # BUGFIX: Only CLIENT and NEW_CLIENT can create appointments
    if request.user.role not in ['CLIENT', 'NEW_CLIENT']:
        msg = 'Randevu oluşturma yetkiniz yok.'
        if request.headers.get('HX-Request'):
            response = HttpResponse(status=403)
            response['HX-Trigger'] = json.dumps({'toast': {'type': 'error', 'message': msg}})
            return response
        return redirect('core:dashboard')
    
    if request.method == 'POST':
        date_str = request.POST.get('date')
        time_str = request.POST.get('time')
        notes = request.POST.get('notes', '').strip()  # BUGFIX: Strip whitespace from notes
        
        if not date_str or not time_str:
            msg = 'Tarih ve saat bilgisi eksik.'
            # BUGFIX: Always use HX-Trigger for HTMX requests (no Django messages)
            if request.headers.get('HX-Request'):
                response = HttpResponse(status=204)
                response['HX-Trigger'] = json.dumps({'toast': {'type': 'error', 'message': msg}})
                return response
            # Non-HTMX fallback: redirect with no message
            return redirect('appointments:calendar')
        
        # BUGFIX: Validate date is not in the past
        try:
            appointment_date = parse_date(date_str)
            if appointment_date < date.today():
                msg = 'Geçmiş tarihler için randevu oluşturamazsınız.'
                if request.headers.get('HX-Request'):
                    response = HttpResponse(status=204)
                    response['HX-Trigger'] = json.dumps({'toast': {'type': 'error', 'message': msg}})
                    return response
                return redirect('appointments:calendar')
        except (ValueError, TypeError):
            msg = 'Geçersiz tarih formatı.'
            if request.headers.get('HX-Request'):
                response = HttpResponse(status=204)
                response['HX-Trigger'] = json.dumps({'toast': {'type': 'error', 'message': msg}})
                return response
            return redirect('appointments:calendar')
        
        # Çakışma kontrolü (Backend tarafında son kontrol)
        # BUGFIX: Use .active() manager for consistency - only active appointments block slots
        is_taken = Appointment.objects.active().filter(
            date=date_str, 
            time=time_str
        ).exists()
        
        if is_taken:
            msg = 'Bu saat maalesef doldu.'
            if request.headers.get('HX-Request'):
                response = HttpResponse(status=204)
                trigger_data = {
                    'toast': {
                        'type': 'error',
                        'message': msg
                    }
                }
                response['HX-Trigger'] = json.dumps(trigger_data)
                return response
        else:
            # BUGFIX: Save notes properly
            Appointment.objects.create(
                client=request.user,
                date=date_str,
                time=time_str,
                notes=notes if notes else None,  # Store None instead of empty string
                status='pending'
            )
            
            # Enhanced success message with appointment details
            appointment_time = parse_date(date_str).strftime('%d %B %Y')
            msg = f'✓ Randevu talebiniz alındı! {appointment_time} - {time_str} için randevunuz onay bekliyor.'
            
            if request.headers.get('HX-Request'):
                # BUGFIX: Don't use HX-Location (causes full reload and breaks navbar)
                # Instead, return 204 with toast and closeModal trigger
                response = HttpResponse(status=204)
                trigger_data = {
                    'toast': {
                        'type': 'success',
                        'message': msg
                    },
                    'closeModal': True  # Custom event to close Bootstrap modal
                }
                response['HX-Trigger'] = json.dumps(trigger_data)
                return response
            
    return redirect('appointments:calendar')

@login_required
def update_status(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    
    # Status parametresini al (URL query string veya POST body)
    new_status = request.GET.get('status') or request.POST.get('status')
    context_type = request.GET.get('context', 'table') # table, card, modal
    
    if not new_status:
        msg = 'Durum belirtilmedi.'
        # BUGFIX: Always use HX-Trigger for HTMX requests (no Django messages)
        if request.headers.get('HX-Request'):
            response = HttpResponse(status=204)
            response['HX-Trigger'] = json.dumps({'toast': {'type': 'error', 'message': msg}})
            return response
        return redirect('appointments:calendar')

    # BUGFIX: Improved authorization and status transition logic
    old_status = appointment.status
    authorized = False
    
    if request.user.role == 'ADMIN':
        # Admin can change to any valid status
        if new_status in ['approved', 'rejected', 'cancelled', 'pending']:
            appointment.status = new_status
            authorized = True
    elif request.user == appointment.client:
        # Clients can only cancel their own appointments if pending or approved
        if new_status == 'cancelled' and old_status in ['pending', 'approved']:
            appointment.status = 'cancelled'
            authorized = True
    
    if not authorized:
        msg = 'Bu işlemi yapmaya yetkiniz yok.'
        if request.headers.get('HX-Request'):
            response = HttpResponse(status=403)
            response['HX-Trigger'] = json.dumps({'toast': {'type': 'error', 'message': msg}})
            return response
        return redirect('appointments:calendar')
    
    appointment.save()
    
    # Generate contextual success message
    status_messages = {
        'approved': f'✓ Randevu onaylandı! {appointment.client.get_full_name()} - {appointment.date.strftime("%d %B")} {appointment.time.strftime("%H:%M")}',
        'rejected': f'Randevu reddedildi: {appointment.client.get_full_name()} - {appointment.date.strftime("%d %B")}',
        'cancelled': f'Randevu iptal edildi: {appointment.date.strftime("%d %B %Y")} {appointment.time.strftime("%H:%M")}',
        'pending': f'Randevu beklemeye alındı: {appointment.date.strftime("%d %B")}',
    }
    success_msg = status_messages.get(new_status, f'Randevu durumu güncellendi: {appointment.get_status_display()}')
    
    if request.headers.get('HX-Request'):
        # BUGFIX: İptal/reddedilen randevuları modal'dan otomatik sil
        if new_status in ['cancelled', 'rejected']:
            # Return empty response with special trigger to remove element
            response = HttpResponse('')
            trigger_data = {
                'toast': {
                    'type': 'success',
                    'message': success_msg
                },
                'removeAppointment': appointment.id  # Custom trigger for removal
            }
            
            # BUGFIX: Eğer bugünkü randevu iptal edildiyse, dashboard widget'ını da güncelle
            from datetime import date
            if appointment.date == date.today():
                trigger_data['updateDashboardWidget'] = True
            
            response['HX-Trigger'] = json.dumps(trigger_data)
            # HTMX will swap with empty content, effectively removing the element
            return response
        
        # BUGFIX: Return correct template based on context
        template_name = 'appointments/partials/admin_row.html'
        if context_type == 'modal':
            template_name = 'appointments/partials/modal_appointment_item.html'
        elif context_type == 'card' or request.user.role == 'CLIENT':
            template_name = 'appointments/partials/client_card.html'
            
        response = render(request, template_name, {'appointment': appointment})
        
        trigger_data = {
            'toast': {
                'type': 'success',
                'message': success_msg
            }
        }
        response['HX-Trigger'] = json.dumps(trigger_data)
        return response
    
    # Non-HTMX fallback: just redirect
    return redirect('appointments:calendar')

# BUGFIX: Added missing list_view for appointments list page
@login_required
def list_view(request):
    """
    Display all appointments in a list format.
    - ADMIN: See all appointments
    - CLIENT/NEW_CLIENT: See only their own appointments
    """
    today = date.today()
    
    if request.user.role == 'ADMIN':
        # BUGFIX: Admin sadece aktif randevuları görür (iptal/red edilenleri değil)
        # Using .active() manager method for consistency
        appointments = Appointment.objects.active().select_related('client').order_by('-date', '-time')
    else:
        # BUGFIX: Clients see only their own appointments (all statuses for history tracking)
        appointments = Appointment.objects.filter(
            client=request.user
        ).order_by('-date', '-time')
    
    context = {
        'appointments': appointments,
        'today': today,
    }
    
    return render(request, 'appointments/list.html', context)
