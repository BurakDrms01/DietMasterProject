from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_POST
from django.contrib import messages
from datetime import date

# Modeller ve Formlar
from .models import Task, TaskCompletion
from .forms import AdminTaskForm 

# --- YARDIMCI FONKSİYONLAR ---
def is_admin(user):
    return user.role == 'ADMIN'

# ==========================================
# CLIENT (DANIŞAN) İŞLEMLERİ
# ==========================================

@login_required
@require_POST 
def toggle_task_completion(request, task_id):
    """
    Danışanın manuel bir görevi tamamlamasını veya geri almasını sağlar.
    HTMX ile çalışır.
    """
    task = get_object_or_404(Task, id=task_id)
    
    # Görevi bul veya oluştur (Tamamlama işlemi)
    completion, created = TaskCompletion.objects.get_or_create(
        user=request.user,
        task=task,
        completion_date=date.today()
    )

    # Eğer zaten varsa sil (Toggle mantığı: Tamamlandı -> Tamamlanmadı)
    if not created:
        completion.delete()
    
    # Dashboard'u yeniden render etmesi için yönlendirme yapıyoruz 
    return redirect('core:dashboard')


# ==========================================
# ADMIN (DİYETİSYEN) İŞLEMLERİ
# ==========================================

@login_required
@user_passes_test(is_admin)
def task_manager(request):
    """
    Diyetisyenin yeni görev eklediği ve mevcut görevleri listelediği sayfa.
    """
    if request.method == 'POST':
        form = AdminTaskForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Görev başarıyla oluşturuldu ve atandı! 🎯")
            return redirect('gamification:manager')
        else:
            messages.error(request, "Formda hata var, lütfen kontrol edin.")
    else:
        form = AdminTaskForm()

    # Mevcut aktif görevleri listele (En son eklenen en üstte)
    existing_tasks = Task.objects.filter(is_active=True).order_by('-id')

    context = {
        'form': form,
        'tasks': existing_tasks
    }
    return render(request, 'gamification/task_manager.html', context)

@login_required
@user_passes_test(is_admin)
def edit_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    
    if request.method == 'POST':
        form = AdminTaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, f"'{task.title}' güncellendi. ✅")
            # Kayıt başarılıysa görev yönetimi sayfasına geri dön
            return redirect('gamification:manager')
    else:
        form = AdminTaskForm(instance=task)

    # BURASI DEĞİŞTİ: Artık partials klasöründeki formu render ediyoruz
    return render(request, 'gamification/partials/task_edit_form.html', {
        'form': form,
        'task': task
    })

@login_required
@user_passes_test(is_admin)
def delete_task(request, task_id):
    """
    Belirtilen görevi veritabanından siler.
    """
    task = get_object_or_404(Task, id=task_id)
    
    # Görevi sil (İsmini mesajda kullanmak için önce alıyoruz)
    title = task.title 
    task.delete()
    
    messages.warning(request, f"'{title}' görevi başarıyla silindi. 🗑️")
    return redirect('gamification:manager')