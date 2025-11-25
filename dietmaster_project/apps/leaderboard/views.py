from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db.models import Sum, OuterRef, Subquery, Value, Count, Q
from django.db.models.functions import Coalesce
from django.utils import timezone
from datetime import timedelta
# Modelleri import ediyoruz
from apps.gamification.models import TaskCompletion, Task

User = get_user_model()

@login_required
def leaderboard_view(request):
    """
    Liderlik Tablosu View'ı:
    - Sıralama, Rozetler, Motivasyon, Rank Booster
    """
    
    # 1. TEMEL AYARLAR
    period = request.GET.get('period', 'daily')
    now = timezone.now()
    
    # Varsayılan (Günlük)
    start_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end_time = now.replace(hour=23, minute=59, second=59, microsecond=999999)
    label = "Günün Şampiyonları 🏆"
    desc = "Bugün en çok puan toplayan danışanlar sıralanıyor."

    # Periyot Ayarı
    if period == 'weekly':
        start_time = (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0)
        label = "Bu Haftanın Liderleri 🔥"
        desc = "Pazartesi gününden bu yana en aktif olanlar."
    elif period == 'monthly':
        start_time = now.replace(day=1, hour=0, minute=0, second=0)
        label = "Bu Ayın Liderleri 👑"
        desc = "Bu ay içindeki genel performans sıralaması."

    # 2. ALT SORGU (PUAN HESABI)
    points_subquery = TaskCompletion.objects.filter(
        user=OuterRef('pk'),
        completion_date__range=(start_time, end_time) # DÜZELDİ: completion_date
    ).values('user').annotate(
        total=Sum('task__points')
    ).values('total')

    # 3. ANA SORGU (KULLANICILARI ÇEKME VE ROZET SAYIMLARI)
    leaderboard_users = User.objects.filter(role='CLIENT').annotate(
        total_points=Coalesce(Subquery(points_subquery), Value(0)),
        
        # Su Görevleri
        water_count=Count('task_completions', filter=Q(
            task_completions__task__task_type='WATER', 
            task_completions__completion_date__range=(start_time, end_time) # DÜZELDİ
        )),
        # Fotoğraf Görevleri
        photo_count=Count('task_completions', filter=Q(
            task_completions__task__task_type='PHOTO', 
            task_completions__completion_date__range=(start_time, end_time) # DÜZELDİ
        )),
        # Toplam Aktivite
        total_tasks_done=Count('task_completions', filter=Q(
            task_completions__completion_date__range=(start_time, end_time) # DÜZELDİ
        ))

    ).order_by('-total_points', 'first_name')

    # 4. PYTHON DÖNGÜSÜ (MOTİVASYON, DNA VE SIRALAMA ANALİZİ)
    ranked_list = list(leaderboard_users)
    
    for i, user in enumerate(ranked_list):
        # A. Takip Modu
        if i > 0:
            prev_user = ranked_list[i-1]
            diff = prev_user.total_points - user.total_points
            user.points_to_pass = diff + 1 if diff >= 0 else 0
        else:
            user.points_to_pass = 0

        # B. DNA Barı
        total_actions = user.water_count + user.photo_count
        if total_actions > 0:
            user.water_pct = (user.water_count / total_actions) * 100
            user.photo_pct = (user.photo_count / total_actions) * 100
        else:
            user.water_pct = 0
            user.photo_pct = 0

        # C. Motivasyon Mesajı
        msg = ""
        if user.total_points == 0:
            msg = "Yarışa katılmak için bir bardak su içerek başla! 💧"
        elif i == 0:
            msg = "Zirvenin sahibi sensin! Kimse seni tutamaz. 👑"
        elif user.points_to_pass > 0 and user.points_to_pass <= 20:
            rival_name = ranked_list[i-1].first_name
            msg = f"Hadi! {rival_name} kişisini geçmene sadece {user.points_to_pass} puan kaldı! 👀"
        elif i < 3:
            msg = "Podyumdasın, harika gidiyorsun! 🌟"
        elif i < 5:
            msg = "Biraz daha zorla, ilk 3'e çok yakınsın! 🔥"
        else:
            msg = "İstikrarlı ilerleyişin sana başarıyı getirecek. 👍"

        if user == request.user:
            user.motivation_msg = f"{user.first_name}, {msg.lower()}"
        else:
            user.motivation_msg = msg

    # 5. KULLANICININ KENDİ SIRASI
    user_rank = 0
    user_points = 0
    for index, user in enumerate(ranked_list, 1):
        if user == request.user:
            user_rank = index
            user_points = user.total_points
            break

    # ==========================================================
    # 🚀 RANK BOOSTER (HATA BURADAYDI, DÜZELTİLDİ)
    # ==========================================================
    
    # A. Bugünün Başlangıç/Bitiş zamanını alalım (zaten start_time/end_time var ama
    # garanti olsun diye 'daily' modundakini tekrar alıyoruz)
    day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    day_end = now.replace(hour=23, minute=59, second=59, microsecond=999999)

    # B. Kullanıcının bugün tamamladığı görev ID'lerini bul
    # HATA BURADAYDI: created_at -> completion_date olarak değiştirildi.
    completed_task_ids = TaskCompletion.objects.filter(
        user=request.user, 
        completion_date__range=(day_start, day_end) 
    ).values_list('task_id', flat=True)
    
    # C. Yapılmayanlardan en yüksek puanlı 3 tanesini seç
    pending_tasks = Task.objects.exclude(
        id__in=completed_task_ids
    ).order_by('-points')[:3]

    # D. Potansiyel kazanç
    potential_gain = sum(t.points for t in pending_tasks)
    
    # E. Haftalık Su Challenge (Simülasyon)
    seven_days_ago = now - timedelta(days=7)
    
    # HATA BURADAYDI: created_at -> completion_date olarak değiştirildi.
    water_streak_days = TaskCompletion.objects.filter(
        user=request.user,
        task__task_type='WATER',
        completion_date__gte=seven_days_ago
    ).dates('completion_date', 'day').count()

    # ==========================================================
    # CONTEXT
    # ==========================================================
    context = {
        'leaderboard': ranked_list,
        'my_rank': user_rank,
        'my_points': user_points,
        'today': now.date(),
        'period': period,
        'label': label,
        'desc': desc,
        'pending_tasks': pending_tasks,
        'potential_gain': potential_gain,
        'water_streak_days': water_streak_days,
    }

    return render(request, 'leaderboard/ranking.html', context)