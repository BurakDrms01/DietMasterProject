from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import DietPlan, PlanRequest
from apps.users.models import CustomUser

@login_required
def pricing_page(request):
    # Kullanıcının zaten bekleyen bir talebi var mı kontrol et
    existing_request = PlanRequest.objects.filter(user=request.user, status='pending').first()
    
    plans = DietPlan.objects.all().order_by('price')
    
    context = {
        'plans': plans,
        'existing_request': existing_request
    }
    return render(request, 'plans/pricing.html', context)

# --- create_plan_request ---
@login_required
def create_plan_request(request, plan_id):
    """
    Kullanıcı paketi seçtiğinde çalışır. 
    Veritabanına KAYIT ETMEZ, sadece seçimi hafızaya alır ve sihirbaza yollar.
    """
    if request.method == 'POST':
        # Paketin var olup olmadığını kontrol et
        plan = get_object_or_404(DietPlan, id=plan_id)
        
        # Zaten bekleyen bir talebi varsa uyar
        existing = PlanRequest.objects.filter(user=request.user, status='pending').exists()
        if existing:
            messages.warning(request, "Zaten onay bekleyen bir paket talebiniz var.")
            return redirect('core:dashboard')
        
        # --- KRİTİK DEĞİŞİKLİK ---
        # Veritabanına kayıt oluşturmuyoruz!
        # Sadece session'a (tarayıcı oturumuna) ID'yi kaydediyoruz.
        request.session['selected_plan_id'] = plan.id
        
        # Profil Sihirbazına Yönlendir
        return redirect('profiles:onboarding_wizard')
            
    return redirect('plans:pricing')

@login_required
def manage_request(request, request_id):
    """Diyetisyenin başvuruyu incelediği ve onayladığı ekran"""
    
    # Sadece Adminler görebilir
    if request.user.role != 'ADMIN':
        return redirect('core:dashboard')

    plan_request = get_object_or_404(PlanRequest, id=request_id)
    profile = plan_request.user.profile # İlişkili profil verisi

    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'approve':
            # 1. Talebi Onayla
            plan_request.status = 'approved'
            plan_request.save()
            
            # 2. Kullanıcıyı 'CLIENT' (Gerçek Danışan) yap
            user = plan_request.user
            user.role = CustomUser.Role.CLIENT
            user.save()
            
            messages.success(request, f"{user.get_full_name()} sisteme danışan olarak kabul edildi! 🎉")
            return redirect('core:dashboard')
            
        elif action == 'reject':
            plan_request.status = 'rejected'
            plan_request.save()
            messages.warning(request, "Başvuru reddedildi.")
            return redirect('core:dashboard')

    return render(request, 'plans/request_detail.html', {
        'req': plan_request,
        'profile': profile
    })