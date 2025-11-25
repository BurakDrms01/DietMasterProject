def dynamic_nav(request):
    if not request.user.is_authenticated:
        return {}

    nav_items = []
    user_role = request.user.role

    if user_role == 'ADMIN':
        nav_items = [
            {'title': 'Anasayfa', 'url_name': 'core:dashboard', 'icon': 'bi-house-door-fill'},
            {'title': 'Danışanlar', 'url_name': '#', 'icon': 'bi-people-fill'},
            {'title': 'Randevular', 'url_name': '#', 'icon': 'bi-calendar-event-fill'},
            {'title': 'Tarif Yönetimi', 'url_name': '#', 'icon': 'bi-journal-richtext'},
        ]
    elif user_role == 'CLIENT':
        nav_items = [
            {'title': 'Anasayfam', 'url_name': 'core:dashboard', 'icon': 'bi-person-fill'},
            {'title': 'Beslenme Planım', 'url_name': '#', 'icon': 'bi-list-check'},
            {'title': 'Gelişim Raporlarım', 'url_name': '#', 'icon': 'bi-graph-up-arrow'},
            {'title': 'Tarifler', 'url_name': '#', 'icon': 'bi-book-fill'},
        ]

    return {'nav_items': nav_items}