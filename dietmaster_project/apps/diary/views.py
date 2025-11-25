from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import MealPhotoForm

@login_required
def upload_meal_photo(request):
    if request.method == 'POST':
        form = MealPhotoForm(request.POST, request.FILES)
        if form.is_valid():
            meal_photo = form.save(commit=False)
            meal_photo.user = request.user
            meal_photo.save()
            return redirect('core:dashboard') # Yüklemeden sonra dashboard'a dön
    # Bu view'ın doğrudan bir GET isteği olmayacak, sadece POST işleyecek.
    # Hatalı durumlarda yine dashboard'a yönlendirebiliriz.
    return redirect('core:dashboard')