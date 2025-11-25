from datetime import datetime, timedelta, time
from calendar import HTMLCalendar
from .models import Appointment, DietitianAvailability

"""
Appointment Slot Logic - IMPORTANT RULES:

1. ACTIVE APPOINTMENTS (block slots):
   - status = 'pending' (awaiting approval)
   - status = 'approved' (confirmed)

2. INACTIVE APPOINTMENTS (do NOT block slots):
   - status = 'cancelled' (user or admin cancelled)
   - status = 'rejected' (admin declined)

3. SLOT AVAILABILITY:
   - Only ACTIVE appointments prevent new bookings
   - Cancelled/rejected appointments are ignored in slot calculations
   - Past appointments should be auto-cancelled by management command

4. LEGACY DATA CLEANUP:
   - Run: python manage.py cleanup_legacy_appointments --auto-cancel-past
   - This ensures old appointments don't block future slots

5. CONSISTENCY:
   - Always use Appointment.objects.active() for slot blocking queries
   - Never use raw .filter(status__in=[...]) - use the manager
"""

class CalendarUtils:
    def __init__(self, year=None, month=None):
        self.year = year or datetime.now().year
        self.month = month or datetime.now().month

    def get_month_days(self):
        """
        Ayın günlerini (hafta hafta) döndürür.
        Her gün için: { 'day': int, 'date': date_obj, 'is_today': bool, 'in_month': bool }
        """
        import calendar
        cal = calendar.Calendar(firstweekday=0) # 0 = Pazartesi
        month_days = []
        
        today = datetime.now().date()

        for week in cal.monthdatescalendar(self.year, self.month):
            week_data = []
            for date_obj in week:
                week_data.append({
                    'day': date_obj.day,
                    'date': date_obj,
                    'is_today': date_obj == today,
                    'in_month': date_obj.month == self.month,
                    'is_past': date_obj < today
                })
            month_days.append(week_data)
        
        return month_days

    @staticmethod
    def get_available_slots(date_obj):
        """
        Belirli bir tarih için müsait saatleri döndürür.
        DietitianAvailability modeline göre dinamik slot üretir.
        """
        slots = []
        weekday = date_obj.weekday()
        
        # 1. Availability Kontrolü
        availabilities = DietitianAvailability.objects.filter(weekday=weekday).order_by('start_time')
        system_has_availability = DietitianAvailability.objects.exists()
        
        # --- FALLBACK: Eğer sistemde hiç availability yoksa eski mantık çalışsın ---
        if not availabilities.exists() and not system_has_availability:
            # Pazar günü kapalı
            if weekday == 6:
                return []

            # Mesai saatlerini belirle
            start_hour = 9
            end_hour = 17 if weekday != 5 else 13 # Cumartesi 13:00'e kadar

            # BUGFIX: Only active appointments (pending/approved) block slots
            # Cancelled/rejected appointments don't prevent new bookings
            # Using .active() manager for consistency
            taken_slots = Appointment.objects.active().filter(
                date=date_obj
            ).values_list('time', flat=True)

            current_time = time(start_hour, 0)
            while current_time.hour < end_hour:
                is_taken = current_time in taken_slots
                
                is_past_time = False
                if date_obj == datetime.now().date():
                    if current_time < datetime.now().time():
                        is_past_time = True

                slots.append({
                    'time': current_time,
                    'display': current_time.strftime('%H:%M'),
                    'is_taken': is_taken,
                    'is_past': is_past_time,
                    'available': not is_taken and not is_past_time
                })
                
                current_time = (datetime.combine(date_obj, current_time) + timedelta(hours=1)).time()
            
            return slots

        # --- DİNAMİK MANTIK ---
        # Eğer sistemde availability var ama bugün için yoksa -> Boş liste döner (Kapalı)
        if not availabilities.exists():
            return []

        # BUGFIX: Only active appointments (pending/approved) block slots
        # Cancelled/rejected appointments don't prevent new bookings
        # Using .active() manager for consistency
        taken_slots = Appointment.objects.active().filter(
            date=date_obj
        ).values_list('time', flat=True)
        
        for av in availabilities:
            current_dt = datetime.combine(date_obj, av.start_time)
            end_dt = datetime.combine(date_obj, av.end_time)
            slot_delta = timedelta(minutes=av.slot_length_minutes)
            
            while current_dt + slot_delta <= end_dt + timedelta(seconds=1):
                slot_time = current_dt.time()
                
                # Çakışma kontrolü
                is_taken = slot_time in taken_slots
                
                # Geçmiş zaman kontrolü
                is_past_time = False
                if date_obj == datetime.now().date():
                    if slot_time < datetime.now().time():
                        is_past_time = True
                
                slots.append({
                    'time': slot_time,
                    'display': slot_time.strftime('%H:%M'),
                    'is_taken': is_taken,
                    'is_past': is_past_time,
                    'available': not is_taken and not is_past_time
                })
                
                current_dt += slot_delta
        
        # Saat sırasına göre diz
        slots.sort(key=lambda x: x['time'])
            
        return slots
