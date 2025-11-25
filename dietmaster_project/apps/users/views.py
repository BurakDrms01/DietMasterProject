from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from datetime import datetime
import traceback
from django.apps import apps  # PatientProfile için

from .forms import ClientRegistrationForm

# ---------------------------------------------------------
# KAYIT OL (REGISTER)
# ---------------------------------------------------------
def register_view(request):
    """
    Yeni kullanıcı kaydı oluşturur.
    """
    # Eğer kullanıcı zaten giriş yapmışsa dashboard'a yönlendir
    if request.user.is_authenticated:
        return redirect('core:dashboard')

    if request.method == 'POST':
        form = ClientRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Kayıttan sonra otomatik giriş yap
            return redirect('core:dashboard')
    else:
        form = ClientRegistrationForm()

    return render(request, 'registration/register.html', {'form': form})


# ---------------------------------------------------------
# PROFİLİM (PROFILE)
# ---------------------------------------------------------
@login_required
def profile_view(request):
    user = request.user

    # PatientProfile modelini dinamik olarak al (circular import riskini azaltır)
    PatientProfile = apps.get_model('profiles', 'PatientProfile')

    # Kullanıcının sağlık profilini garanti altına al
    profile, created = PatientProfile.objects.get_or_create(user=user)

    if request.method == 'POST':
        try:
            # --- 1) USER ALANLARI ---
            first_name = request.POST.get('first_name', '').strip()
            last_name  = request.POST.get('last_name', '').strip()
            phone      = request.POST.get('phone_number', '').strip()

            user.first_name   = first_name
            user.last_name    = last_name
            user.phone_number = phone

            if 'profile_photo' in request.FILES:
                user.profile_photo = request.FILES['profile_photo']

            user.save()

            # --- 2) PATIENTPROFILE ALANLARI ---
            birth_date_str = request.POST.get('birth_date', '').strip()
            gender         = request.POST.get('gender', '').strip()

            # Doğum tarihi hatalı girilirse özel mesaj ver
            if birth_date_str:
                try:
                    profile.birth_date = datetime.strptime(
                        birth_date_str,
                        "%Y-%m-%d"
                    ).date()
                except ValueError:
                    # Sadece tarih için anlamlı bir uyarı göster
                    return HttpResponse("""
                        <div class="alert alert-danger alert-dismissible fade show position-fixed top-0 end-0 m-3 shadow-lg" role="alert" style="z-index: 1050;">
                            <strong>Geçersiz tarih!</strong> Lütfen doğum tarihini geçerli bir formatta girin. <br>
                            <small>Örnek: 2000-05-07 (YYYY-AA-GG)</small>
                            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                        </div>
                    """)

            # Cinsiyet (M / F)
            if gender in ['M', 'F']:
                profile.gender = gender

            profile.save()

            return HttpResponse("""
                <div class="alert alert-success alert-dismissible fade show position-fixed top-0 end-0 m-3 shadow-lg" role="alert" style="z-index: 1050;">
                    <i class="bi bi-check-circle-fill me-2"></i> Bilgiler başarıyla kaydedildi!
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                </div>
            """)

        except Exception as e:
            # Terminal log'u dursun ama kullanıcıya iç hata detayını göstermeyelim
            print("------------------------------------------------")
            print("PROFIL GÜNCELLEME HATASI OLUŞTU:")
            print(traceback.format_exc())
            print("------------------------------------------------")

            return HttpResponse("""
                <div class="alert alert-danger alert-dismissible fade show position-fixed top-0 end-0 m-3 shadow-lg" role="alert" style="z-index: 1050;">
                    <strong>Beklenmeyen bir hata oluştu.</strong> Lütfen tekrar deneyin. <br>
                    <small>Hata devam ederse destek ekibiyle iletişime geçebilirsiniz.</small>
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                </div>
            """)

    return render(request, 'users/profile.html', {
        'user': user,
        'profile': profile,
    })