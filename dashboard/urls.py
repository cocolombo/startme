from django.urls import path
from . import views

urlpatterns = [
    # =================================
    # VUES PRINCIPALES
    # =================================
    path('', views.index, name='index_root'),

    # =================================
    # ACTIONS SUR LES PAGES
    # =================================
    path('page/create/', views.create_page, name='create_page'),
    path('page/rename/<int:page_id>/', views.rename_page, name='rename_page'),
    path('page/delete/<int:page_id>/', views.delete_page, name='delete_page'),
    path('page/<slug:slug>/', views.index, name='index'), # Doit être après les autres URLs de page

    # =================================
    # ACTIONS SUR LES WIDGETS
    # =================================
    path('widget/add/<int:page_id>/', views.add_widget, name='add_widget'),
    path('widget/delete/<int:widget_id>/', views.delete_widget, name='delete_widget'),
    path('widget/<int:pk>/rename/', views.rename_widget, name='rename_widget'),
    path('widget/move/<int:widget_id>/', views.move_widget_to_page, name='move_widget'),
    path('widget/toggle-width/<int:widget_id>/', views.toggle_widget_width, name='toggle_widget_width'),

    # =================================
    # ACTIONS SUR LES LIENS
    # =================================
    path('link/add/<int:widget_id>/', views.add_link, name='add_link'),
    path('link/delete/<int:link_id>/', views.delete_link, name='delete_link'),
    path('link/<int:pk>/edit/', views.edit_link, name='edit_link'),
    path('link/<int:pk>/cancel/', views.cancel_edit_link, name='cancel_edit_link'),
    path('link/run/<int:link_id>/', views.run_command, name='run_command'),
    path('link/open-local/<int:link_id>/', views.open_local_file, name='open_local_file'),

    # =================================
    # API (pour HTMX / JavaScript)
    # =================================
    path('api/update-page-order/', views.update_page_order, name='update_page_order'),
    path('api/update-widget-order/', views.update_widget_order, name='update_widget_order'),
    path('api/update-order/', views.update_link_order, name='update_order'), # Correction ici
    path('api/move-link/<int:link_id>/', views.move_link_to_page, name='move_link'),
    path('api/save-note/<int:widget_id>/', views.save_note_content, name='save_note'),

    # =================================
    # UTILITAIRES
    # =================================
    path('api/search/', views.search, name='search'),
    path('api/system-monitor/', views.system_monitor, name='system_monitor'),
    path('api/network-info/', views.get_network_info, name='get_network_info'),
    path('api/backup/', views.download_backup, name='download_backup'),
]
