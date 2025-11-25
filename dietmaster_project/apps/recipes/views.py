from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from .models import Recipe, Category
from .forms import RecipeForm

@login_required
def recipe_list(request):
    category_slug = request.GET.get('category')
    filter_status = request.GET.get('status', 'APPROVED') # Varsayılan: Onaylılar
    
    # Temel Sorgu
    recipes = Recipe.objects.select_related('category', 'author')
    
    # EĞER ADMİN DEĞİLSE SADECE ONAYLILARI GÖRÜR
    if request.user.role != 'ADMIN':
        recipes = recipes.filter(status='APPROVED')
    else:
        # Admin ise tabdan gelen filtreye bak (APPROVED veya PENDING)
        if filter_status in ['APPROVED', 'PENDING']:
            recipes = recipes.filter(status=filter_status)

    # Kategori Filtresi
    if category_slug:
        recipes = recipes.filter(category__slug=category_slug)

    categories = Category.objects.all()

    context = {
        'recipes': recipes,
        'categories': categories,
        'active_category': category_slug,
        'active_status': filter_status, # Tab kontrolü için
        'pending_count': Recipe.objects.filter(status='PENDING').count() if request.user.role == 'ADMIN' else 0
    }

    if request.headers.get('HX-Request'):
        return render(request, 'recipes/partials/recipe_grid.html', context)
    
    return render(request, 'recipes/recipe_list.html', context)

@login_required
def recipe_detail(request, pk):
    # Admin değilse ve tarif onaylı değilse görmesin
    recipe = get_object_or_404(Recipe, pk=pk)
    if request.user.role != 'ADMIN' and recipe.status != 'APPROVED':
        return HttpResponseForbidden("Bu tarifi görüntüleme yetkiniz yok.")

    related_recipes = Recipe.objects.filter(category=recipe.category, status='APPROVED').exclude(pk=pk)[:3]
    
    return render(request, 'recipes/recipe_detail.html', {'recipe': recipe, 'related_recipes': related_recipes})

@login_required
def add_recipe(request):
    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES)
        if form.is_valid():
            recipe = form.save(commit=False)
            recipe.author = request.user
            
            # Rol Kontrolü: Admin ise direkt yayınla, Danışan ise Onay Beklesin
            if request.user.role == 'ADMIN':
                recipe.status = 'APPROVED'
                messages.success(request, "Tarif başarıyla yayınlandı! 🎉")
            else:
                recipe.status = 'PENDING'
                messages.info(request, "Tarifiniz gönderildi ve diyetisyen onayına sunuldu. Teşekkürler! ⏳")
            
            recipe.save()
            return redirect('recipes:list')
    else:
        form = RecipeForm()

    return render(request, 'recipes/recipe_form.html', {'form': form})

@login_required
def review_recipe(request, pk, action):
    # Sadece Adminler Onaylayabilir/Reddedebilir
    if request.user.role != 'ADMIN':
        return HttpResponseForbidden()
        
    recipe = get_object_or_404(Recipe, pk=pk)
    
    if action == 'approve':
        recipe.status = 'APPROVED'
        messages.success(request, f"{recipe.title} onaylandı.")
    elif action == 'reject':
        recipe.status = 'REJECTED'
        messages.warning(request, f"{recipe.title} reddedildi.")
        
    recipe.save()
    
    # HTMX ile listeyi yenile
    # PENDING listesini yeniden çekip render ediyoruz
    recipes = Recipe.objects.filter(status='PENDING').select_related('category', 'author')
    return render(request, 'recipes/partials/recipe_grid.html', {'recipes': recipes, 'active_status': 'PENDING'})