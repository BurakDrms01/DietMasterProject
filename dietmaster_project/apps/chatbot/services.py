import google.generativeai as genai
import PIL.Image  # <--- YENİ: Resim işleme için gerekli
from django.conf import settings
from django.apps import apps 

class ChatService:
    def __init__(self):
        try:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.model = genai.GenerativeModel(settings.GEMINI_MODEL_NAME)
        except Exception as e:
            print(f"AI Config Error: {e}")
            self.model = None

    def calculate_needs(self, weight, height, age=30):
        """
        Su ve kalori hesaplar. Eğer kilo/boy yoksa güvenli çıkış yapar.
        """
        if not weight or not height or weight <= 0 or height <= 0:
            return None, None
        
        try:
            water_liters = round(float(weight) * 0.033, 1)
            bmr = (10 * float(weight)) + (6.25 * float(height)) - (5 * age) + 5
            tdee = int(bmr * 1.2) 
            return water_liters, tdee
        except Exception as e:
            print(f"HESAPLAMA HATASI: {e}")
            return None, None

    def get_user_health_data(self, user):
        try:
            PatientProfile = apps.get_model('profiles', 'PatientProfile')
            profile = PatientProfile.objects.filter(user=user).first()
            
            if not profile:
                print(f"DEBUG: {user.username} için profil bulunamadı.")
                return f"DURUM: Kullanıcı ({user.first_name}) sistemde kayıtlı ama sağlık profilini henüz oluşturmamış."

            if not profile.weight or not profile.height:
                return f"DURUM: Kullanıcının profili var ama Kilo veya Boy bilgisini girmemiş."

            water_need, calorie_need = self.calculate_needs(profile.weight, profile.height)
            
            diseases = profile.chronic_diseases if profile.chronic_diseases else "Bilinen yok"
            allergies = profile.allergies if profile.allergies else "Bilinen yok"
            activity = profile.get_activity_level_display()
            
            context = f"""
            === DANIŞAN KİMLİK KARTI ===
            Adı: {user.first_name}
            Mevcut Kilo: {profile.weight} kg
            Boy: {profile.height} cm
            
            === HESAPLANMIŞ İDEAL DEĞERLER ===
            * Önerilen Günlük Su: {water_need if water_need else 'Hesaplanamadı'} Litre
            * Tahmini Kalori İhtiyacı: {calorie_need if calorie_need else 'Hesaplanamadı'} kcal
            
            === SAĞLIK DURUMU ===
            Aktivite: {activity}
            Rahatsızlıklar: {diseases}
            Alerjiler: {allergies}
            ==============================
            """
            return context

        except Exception as e:
            print(f"KRİTİK HATA (services.py): {str(e)}")
            return "DURUM: Teknik bir hata nedeniyle profil verisine ulaşılamadı."

    def generate_response(self, user, user_message, image_file=None):
        if not self.model:
            return "Sistem şu an bakımda."

        health_context = self.get_user_health_data(user)

        # Eğer resim varsa, prompt'a özel talimat ekle
        image_instruction = ""
        if image_file:
            image_instruction = """
            [GÖRSEL ANALİZ MODU AKTİF]
            Kullanıcı sana bir yemek veya besin fotoğrafı gönderdi.
            1. Fotoğraftaki yemeği tanımla.
            2. İçindekileri ve tahmini kaloriyi analiz et.
            3. Kullanıcının sağlık profiline uygun olup olmadığını yorumla.
            """

        system_prompt = f"""
        ROLÜN:
        Sen 'DietMaster' uygulamasının koçluk yapan, samimi ve şeffaf yapay zeka diyetisyenisin.
        
        BAĞLAM (KULLANICI VERİLERİ):
        {health_context}
        
        {image_instruction}

        KURALLAR:
        1. **İSİMLE HİTAP:** Cevabına mutlaka "{user.first_name}" diyerek başla.
        2. **VERİ KULLAN:** Hesaplanan su ve kalori değerlerini kesinlikle kullan.
        3. **NEDENİNİ AÇIKLA:** Kullanıcı sorarsa hesaplamanın mantığını anlat.
        4. **GÖRSEL:** Resim varsa önce onu yorumla.
        5. **EMPATİ:** Motive edici ol.

        KULLANICI SORUSU:
        {user_message}
        """

        try:
            # GÜNCELLENEN KISIM: Resim varsa list olarak gönder
            if image_file:
                img = PIL.Image.open(image_file)
                # Gemini'ye [Prompt, Resim] şeklinde liste veriyoruz
                response = self.model.generate_content([system_prompt, img])
            else:
                response = self.model.generate_content(system_prompt)
                
            return response.text
        except Exception as e:
            print(f"AI RESPONSE ERROR: {e}")
            return f"Üzgünüm, şu an cevap üretemiyorum. Hata: {str(e)}"