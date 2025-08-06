from users.services import menu_sidebar 

def menu_items_processor(request):
    if request.user.is_authenticated:
        return menu_sidebar(request)
    return {}
