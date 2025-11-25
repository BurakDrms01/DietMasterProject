import google.generativeai as genai
from django.conf import settings
from apps.profiles.models import PatientProfile

# API ANAHTARINI BURAYA YAPIŞTIR (Veya settings'den çek)
GOOGLE_API_KEY = "Guvenlikicinsildimsimdilik" 

def get_ai_response(user, user_message):
    """
    Google Gemini API kullanarak, kullanıcının sağlık profiline göre
    kişiselleştirilmiş cevap üretir.
    """
    try:
        # 1. Profil Verilerini Çek
        profile = user.profile
        
        # Kullanıcı hakkında AI'ya vereceğimiz "Gizli Bilgi Fişi" (Context)
        user_context = f"""
        SENİN ROLÜN:
        Sen 'DietMaster' adında profesyonel, motive edici ve arkadaş canlısı bir AI Diyetisyensin.
        Kullanıcıyla konuşurken aşağıdaki verilere göre kişiselleştirilmiş tavsiyeler ver.
        Asla tıbbi teşhis koyma, sadece beslenme ve yaşam tarzı önerisi ver.

        KULLANICI BİLGİLERİ:
        - İsim: {user.first_name}
        - Mevcut Kilo: {profile.weight} kg
        - Hedef Kilo: {profile.goal_weight} kg
        - BMI Durumu: {profile.bmi_status}
        - Günlük Aktivite: {profile.get_activity_level_display()}
        - Alerjiler/Yasaklar: {profile.allergies if profile.allergies else 'Yok'}
        - Sevmediği Besinler: {profile.disliked_foods if profile.disliked_foods else 'Yok'}
        - Kronik Rahatsızlık: {profile.chronic_diseases if profile.chronic_diseases else 'Yok'}

        Soru: {user_message}
        """

        # 2. Gemini Ayarları
        genai.configure(api_key=GOOGLE_API_KEY)
        model = genai.GenerativeModel('gemini-1.0-pro')



        # 3. Cevabı Üret
        response = model.generate_content(user_context)
        
        return response.text

    except PatientProfile.DoesNotExist:
        return "Profil bilgilerinize ulaşamadım. Lütfen önce 'Sağlık Karnesi' veya 'Ayarlar' kısmından profilinizi oluşturun."
    except Exception as e:
        return f"Üzgünüm, şu an bağlantımda bir sorun var. (Hata: {str(e)})"