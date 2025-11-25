from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.utils import timezone
import json

# Modeller
from .models import DailyWaterIntake, PatientProfile
from apps.plans.models import DietPlan, PlanRequest # Paket Seçimi İçin

# Formlar
from .forms import ProfileUpdateForm, OnboardingForm

@login_required
def my_profile(request):
    # Profil yoksa oluştur
    profile, created = PatientProfile.objects.get_or_create(user=request.user)
    
    # --- KİLO GRAFİĞİ VERİSİ ---
    history = profile.weight_history.all()
    dates = [h.date.strftime('%d %b') for h in history]
    weights = [float(h.weight) for h in history]
    
    # Profil güncelleme formu
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profil güncellendi!")
            return redirect('profiles:detail')
    else:
        form = ProfileUpdateForm(instance=profile)
    
    context = {
        'profile': profile,
        'user': request.user,
        'form': form,
        'chart_dates': json.dumps(dates),
        'chart_weights': json.dumps(weights),
        'chart_goal': json.dumps(float(profile.goal_weight)) if profile.goal_weight else "null",
    }
    return render(request, 'profiles/profile_detail.html', context)

# --- SU EKLEME VIEW (HTMX) ---
@login_required
def add_water(request, amount):
    water_record, created = DailyWaterIntake.objects.get_or_create(
        user=request.user,
        date=timezone.now().date()
    )

    if request.method == "POST" and amount > 0:
        water_record.current_amount += amount
        water_record.save()
    
    return render(request, 'profiles/partials/water_widget.html', {'water': water_record})

# --- SİHİRBAZ (ONBOARDING) VIEW ---
@login_required
def onboarding_wizard(request):
    profile, created = PatientProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = OnboardingForm(request.POST, instance=profile)
        if form.is_valid():
            # 1. Profili Kaydet
            profile = form.save(commit=False)
            profile.is_onboarding_complete = True
            profile.save()
            
            # 2. Session'dan Seçilen Paketi Al ve Talep Oluştur
            plan_id = request.session.get('selected_plan_id')
            
            if plan_id:
                try:
                    plan = DietPlan.objects.get(id=plan_id)
                    PlanRequest.objects.create(
                        user=request.user, 
                        plan=plan,
                        status='pending'
                    )
                    # Session'dan temizle
                    del request.session['selected_plan_id']
                    
                    # --- KRİTİK GÜNCELLEME ---
                    # Frontend'in yakalayıp Modalı açması için özel anahtar kelime gönderiyoruz:
                    messages.success(request, 'application_submitted')
                    
                except DietPlan.DoesNotExist:
                    messages.error(request, "Seçilen paket bulunamadı.")
            else:
                # Paket seçilmeden geldiyse (Nadir durum)
                messages.info(request, "Profilin güncellendi.")

            return redirect('core:dashboard')
    else:
        form = OnboardingForm(instance=profile)

    return render(request, 'profiles/wizard.html', {'form': form})