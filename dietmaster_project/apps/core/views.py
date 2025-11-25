from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from datetime import date
from django.db.models import Q

# Gerekli Modeller
from apps.plans.models import PlanRequest
from apps.nutrition.models import DietProgram, DailyMealPlan
from apps.gamification.models import Task, TaskCompletion 
from apps.profiles.models import DailyWaterIntake  # Su takibi
from apps.appointments.models import Appointment   # Randevu sistemi

# Aktif User modelini alıyoruz
User = get_user_model()


@login_required
def dashboard(request):
    user = request.user
    user_role = user.role
    today = date.today()
    
    # Temel context verisi
    context = {
        'user_role': user_role,
        'user': user
    }
    
    # ==========================================
    # 1. ADMİN (DİYETİSYEN) DASHBOARD
    # ==========================================
    if user_role == 'ADMIN':
        # A. İstatistikler
        aktif_danisan_sayisi = User.objects.filter(role='CLIENT').count()
        bekleyen_talep_sayisi = PlanRequest.objects.filter(status='pending').count()
        
        # B. Bekleyen Başvurular Tablosu (Sadece son 5 tanesi - Özet)
        bekleyen_talepler = (
            PlanRequest.objects
            .filter(status='pending')
            .select_related('user', 'plan', 'user__profile')
            .order_by('-created_at')[:5]
        )

        # C. Bugünkü Randevular (Sadece aktif randevular - iptal/red edilenler hariç)
        # Appointment modelindeki custom manager'ı kullanıyoruz
        bugunku_randevular = (
            Appointment.objects.active()
            .for_date(today)
            .select_related('client')
            .order_by('time')
        )
        
        context['aktif_danisan_sayisi'] = aktif_danisan_sayisi
        context['yeni_basvuru_sayisi'] = bekleyen_talep_sayisi
        context['bekleyen_talepler'] = bekleyen_talepler
        context['bugunku_randevu_sayisi'] = bugunku_randevular.count()
        context['bugunku_randevular'] = bugunku_randevular
        context['okunmamis_mesaj_sayisi'] = 0  # Şimdilik sabit, mesaj sistemi entegre olunca güncellenebilir
        
        return render(request, 'core/dashboard_admin.html', context)

    # ==========================================
    # 2. CLIENT (AKTİF DANIŞAN) DASHBOARD
    # ==========================================
    elif user_role == 'CLIENT':
        
        # A. GÖREV YÖNETİMİ (GAMIFICATION)
        all_tasks = (
            Task.objects
            .filter(is_active=True, start_date__lte=today)
            .filter(Q(end_date__gte=today) | Q(end_date__isnull=True))
            .filter(Q(is_for_everyone=True) | Q(assigned_users=user))
            .distinct()
        )
        
        # Tamamlanan görevler
        completed_tasks_today = (
            TaskCompletion.objects
            .filter(user=user, completion_date=today)
            .select_related('task', 'meal_photo')
        )
        
        completed_tasks_map = {comp.task.id: comp for comp in completed_tasks_today}

        # İstatistik Hesaplama
        points_today = sum(comp.task.points for comp in completed_tasks_today)
        total_tasks_count = all_tasks.count()
        completed_tasks_count = len(completed_tasks_map)
        max_points_today = sum(task.points for task in all_tasks)
        
        progress_percent = int((points_today / max_points_today) * 100) if max_points_today > 0 else 0
        
        # B. BESLENME PROGRAMI (GÜNLÜK MENÜ)
        weekday_index = today.weekday()  # 0=Pazartesi, 6=Pazar

        # Aktif ve tarihi geçerli olan programı bul
        active_program = (
            DietProgram.objects
            .filter(
                user=user,
                is_active=True,
                start_date__lte=today,
                end_date__gte=today
            )
            .first()
        )

        todays_meal_plan = None
        if active_program:
            # Program varsa, bugüne ait yemekleri çek
            todays_meal_plan = (
                DailyMealPlan.objects
                .filter(program=active_program, day_of_week=weekday_index)
                .first()
            )

        # C. SU TAKİBİ
        # Bugün için su kaydını getir veya oluştur
        water_record, created = DailyWaterIntake.objects.get_or_create(
            user=user,
            date=today
        )

        # D. GELECEK RANDEVU
        # Sadece aktif (pending/approved) randevular içinden, bugünden itibaren en yakını
        upcoming_appointment = (
            Appointment.objects.active()
            .filter(client=user, date__gte=today)
            .order_by('date', 'time')
            .first()
        )

        # Context Doldurma
        context.update({
            'all_tasks': all_tasks,
            'completed_tasks_map': completed_tasks_map,
            'points_today': points_today,
            'max_points_today': max_points_today,
            'completed_tasks_count': completed_tasks_count,
            'total_tasks_count': total_tasks_count,
            'progress_percent': progress_percent,
            'todays_meal_plan': todays_meal_plan,      # Menü verisi
            'water_record': water_record,              # Su verisi (Widget ve Görev Kartı için)
            'upcoming_appointment': upcoming_appointment,  # Gelecek randevu
        })
        
        return render(request, 'core/dashboard_client.html', context)

    # ==========================================
    # 3. NEW_CLIENT (ADAY / YENİ ÜYE) DASHBOARD
    # ==========================================
    elif user_role == 'NEW_CLIENT':
        # Kullanıcının son paket başvurusunu çek (Varsa durumunu göstereceğiz)
        latest_request = PlanRequest.objects.filter(user=user).last()
        
        # Gelecek randevu (Varsa)
        upcoming_appointment = (
            Appointment.objects.active()
            .filter(client=user, date__gte=today)
            .order_by('date', 'time')
            .first()
        )
            
        context['welcome_message'] = f"Hoş Geldin, {user.first_name}!"
        context['plan_request'] = latest_request 
        context['upcoming_appointment'] = upcoming_appointment
            
        return render(request, 'core/dashboard_new_client.html', context)
            
    else:
        # Fallback (Örn: Staff, ileride STAFF için ayrı dashboard açılabilir)
        return render(request, 'core/dashboard_admin.html', context)


@login_required
def bugunku_randevu_widget(request):
    """
    HTMX partial view: Bugünkü randevu sayacını render eder.
    Dashboard'daki widget'ı güncellemek için kullanılır.
    Sadece ADMIN rolü için anlamlıdır.
    """
    if request.user.role != 'ADMIN':
        # Admin olmayanlar için her zaman 0 dön
        return render(
            request,
            'core/partials/bugunku_randevu_widget.html',
            {'bugunku_randevu_sayisi': 0}
        )
    
    today = date.today()
    bugunku_randevu_sayisi = Appointment.objects.active().for_date(today).count()
    
    context = {'bugunku_randevu_sayisi': bugunku_randevu_sayisi}
    return render(request, 'core/partials/bugunku_randevu_widget.html', context)
