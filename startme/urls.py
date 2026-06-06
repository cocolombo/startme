
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_not_required
from django.urls import path, include  # <--- Notez l'ajout de 'include' ici

urlpatterns = [
    path('admin/', admin.site.urls),

    # Authentification.
    # La page de login doit rester accessible sans être connecté, sinon
    # LoginRequiredMiddleware créerait une boucle de redirection infinie.
    path(
        'accounts/login/',
        login_not_required(auth_views.LoginView.as_view()),
        name='login',
    ),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),

    # Cette ligne dit : "Pour la page d'accueil (vide), va chercher les URLs du dashboard"
    path('', include('dashboard.urls')),
]
