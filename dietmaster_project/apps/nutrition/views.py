from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from datetime import date  # --- EKSİK OLAN BU SATIRDI ---
from .models import DietProgram, DailyMealPlan
from .forms import DietProgramForm, DailyMealForm

User = get_user_model()

@login_required
def program_create(request, client_id):
    """Yeni bir diyet programı başlığı oluşturur"""
    # Sadece Admin (Diyetisyen) erişebilir
    if request.user.role != 'ADMIN':
        return redirect('core:dashboard')

    client = get_object_or_404(User, id=client_id)
    
    if request.method == 'POST':
        form = DietProgramForm(request.POST)
        if form.is_valid():
            program = form.save(commit=False)
            program.user = client
            program.save()
            
            # Otomatik olarak 7 günü de boş olarak oluştur
            for i in range(7):
                DailyMealPlan.objects.create(program=program, day_of_week=i)
                
            messages.success(request, f"{client.get_full_name()} için program oluşturuldu. Şimdi detayları girin.")
            return redirect('nutrition:program_edit', program_id=program.id)
    else:
        form = DietProgramForm()
        
    return render(request, 'nutrition/program_create.html', {'form': form, 'client': client})

@login_required
def program_edit(request, program_id):
    """Oluşturulan programın günlerini düzenleyen EDITÖR"""
    # Sadece Admin erişebilir
    if request.user.role != 'ADMIN':
        return redirect('core:dashboard')

    program = get_object_or_404(DietProgram, id=program_id)
    days = program.daily_plans.all().order_by('day_of_week')
    
    # Varsayılan olarak ilk günü veya seçilen günü getir
    selected_day_id = request.GET.get('day_id')
    
    if selected_day_id:
        active_day = get_object_or_404(DailyMealPlan, id=selected_day_id)
    else:
        active_day = days.first()

    if request.method == 'POST':
        form = DailyMealForm(request.POST, instance=active_day)
        if form.is_valid():
            form.save()
            messages.success(request, f"{active_day.get_day_of_week_display()} güncellendi!")
            return redirect(f"{request.path}?day_id={active_day.id}")
    else:
        form = DailyMealForm(instance=active_day)

    return render(request, 'nutrition/program_editor.html', {
        'program': program,
        'days': days,
        'active_day': active_day,
        'form': form
    })

@login_required
def client_list(request):
    """Diyetisyenin danışanlarını listelediği sayfa"""
    # Sadece Admin erişebilir
    if request.user.role != 'ADMIN':
        return redirect('core:dashboard')

    danisanlar = User.objects.filter(role='CLIENT').select_related('profile')
    
    danisan_listesi = []
    for danisan in danisanlar:
        aktif_program = DietProgram.objects.filter(user=danisan, is_active=True).first()
        danisan_listesi.append({
            'user': danisan,
            'program': aktif_program
        })

    return render(request, 'nutrition/client_list.html', {
        'danisan_listesi': danisan_listesi
    })

@login_required
def my_plan(request):
    """Danışanın tüm beslenme programını gördüğü sayfa"""
    # Sadece Client erişebilir
    if request.user.role != 'CLIENT':
        return redirect('core:dashboard')

    today = date.today()
    
    # Aktif ve tarihi geçerli olan programı bul
    active_program = DietProgram.objects.filter(
        user=request.user, 
        is_active=True, 
        start_date__lte=today, 
        end_date__gte=today
    ).first()
    
    days = []
    if active_program:
        days = active_program.daily_plans.all().order_by('day_of_week')

    return render(request, 'nutrition/my_plan.html', {
        'program': active_program,
        'days': days,
        'today_index': today.weekday() # 0=Pzt, 6=Pazar
    })