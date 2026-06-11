"""Tests verrouillant les correctifs de la revue de sécurité.

Chaque classe cible une faille corrigée :
- AuthenticationTests        → #1  (LoginRequiredMiddleware)
- CsrfProtectionTests        → #5  (retrait de @csrf_exempt)
- EditLinkValidationTests    → #6  (edit_link ne doit plus écrire None)
- ReorderTests               → #7 + #8 (filter(id__in) + bulk_update)
- SafeRefererTests           → #10 (_safe_referer contre l'open-redirect)
"""

from unittest.mock import Mock, patch

import requests

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from . import views
from .models import Link, Page, Widget, next_order


class BaseTestCase(TestCase):
    """Fixtures communes : un utilisateur connecté, une page et un widget."""

    def setUp(self) -> None:
        self.user = User.objects.create_user(username='tester', password='secret123')
        self.client.force_login(self.user)

        self.page = Page.objects.create(name='Accueil', slug='accueil', order=0)
        self.widget = Widget.objects.create(
            title='Liens', page=self.page, order=0, widget_type='list'
        )


class AuthenticationTests(TestCase):
    """#1 — LoginRequiredMiddleware protège toutes les vues."""

    def setUp(self) -> None:
        self.page = Page.objects.create(name='Accueil', slug='accueil', order=0)

    def test_anonyme_redirige_vers_login(self) -> None:
        response = self.client.get(reverse('index_root'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)

    def test_page_login_accessible_sans_connexion(self) -> None:
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

    def test_utilisateur_connecte_accede_au_dashboard(self) -> None:
        user = User.objects.create_user(username='tester', password='secret123')
        self.client.force_login(user)
        response = self.client.get(reverse('index_root'))
        self.assertEqual(response.status_code, 200)


class CsrfProtectionTests(BaseTestCase):
    """#5 — sans @csrf_exempt, un POST sans token est rejeté (403)."""

    def setUp(self) -> None:
        super().setUp()
        # Client qui applique réellement la vérification CSRF.
        self.csrf_client = Client(enforce_csrf_checks=True)
        self.csrf_client.force_login(self.user)

    def test_post_sans_token_csrf_est_rejete(self) -> None:
        response = self.csrf_client.post(
            reverse('update_order'),
            {'widget_id': self.widget.id, 'link': []},
        )
        self.assertEqual(response.status_code, 403)


class EditLinkValidationTests(BaseTestCase):
    """#6 — edit_link valide les entrées et n'écrit jamais None."""

    def test_titre_vide_sur_liste_renvoie_400_et_ne_modifie_rien(self) -> None:
        link = Link.objects.create(
            title='Original', url='https://exemple.com', widget=self.widget, order=0
        )
        response = self.client.post(
            reverse('edit_link', args=[link.id]),
            {'title': '', 'url': 'https://exemple.com'},
        )
        self.assertEqual(response.status_code, 400)
        link.refresh_from_db()
        self.assertEqual(link.title, 'Original')

    def test_snippet_sans_url_renvoie_400(self) -> None:
        snippet_widget = Widget.objects.create(
            title='Commandes', page=self.page, order=1, widget_type='snippet'
        )
        link = Link.objects.create(
            title='Cmd', url='ls -la', widget=snippet_widget, order=0
        )
        response = self.client.post(
            reverse('edit_link', args=[link.id]),
            {'title': 'Cmd', 'url': ''},
        )
        self.assertEqual(response.status_code, 400)
        link.refresh_from_db()
        self.assertEqual(link.url, 'ls -la')

    def test_edition_valide_met_a_jour_le_lien(self) -> None:
        link = Link.objects.create(
            title='Original', url='https://exemple.com', widget=self.widget, order=0
        )
        response = self.client.post(
            reverse('edit_link', args=[link.id]),
            {'title': 'Nouveau', 'url': 'https://nouveau.com'},
        )
        self.assertEqual(response.status_code, 200)
        link.refresh_from_db()
        self.assertEqual(link.title, 'Nouveau')
        self.assertEqual(link.url, 'https://nouveau.com')


class ReorderTests(BaseTestCase):
    """#7 + #8 — réordonnancement robuste via filter(id__in) + bulk_update."""

    def test_update_link_order_applique_position_et_widget(self) -> None:
        autre_widget = Widget.objects.create(
            title='Autre', page=self.page, order=1, widget_type='list'
        )
        l1 = Link.objects.create(title='A', url='a', widget=self.widget, order=0)
        l2 = Link.objects.create(title='B', url='b', widget=self.widget, order=1)

        response = self.client.post(
            reverse('update_order'),
            {'widget_id': autre_widget.id, 'link': [l2.id, l1.id]},
        )
        self.assertEqual(response.status_code, 200)

        l1.refresh_from_db()
        l2.refresh_from_db()
        # Nouveau parent pour les deux liens.
        self.assertEqual(l1.widget_id, autre_widget.id)
        self.assertEqual(l2.widget_id, autre_widget.id)
        # Ordre = position dans la liste envoyée (l2 puis l1).
        self.assertEqual(l2.order, 0)
        self.assertEqual(l1.order, 1)

    def test_update_link_order_ignore_les_ids_inexistants(self) -> None:
        l1 = Link.objects.create(title='A', url='a', widget=self.widget, order=0)
        response = self.client.post(
            reverse('update_order'),
            {'widget_id': self.widget.id, 'link': [l1.id, 999999]},
        )
        self.assertEqual(response.status_code, 200)
        l1.refresh_from_db()
        self.assertEqual(l1.order, 0)

    def test_update_widget_order_applique_les_positions(self) -> None:
        w2 = Widget.objects.create(
            title='W2', page=self.page, order=1, widget_type='list'
        )
        response = self.client.post(
            reverse('update_widget_order'),
            {'widget': [w2.id, self.widget.id]},
        )
        self.assertEqual(response.status_code, 200)
        w2.refresh_from_db()
        self.widget.refresh_from_db()
        self.assertEqual(w2.order, 0)
        self.assertEqual(self.widget.order, 1)

    def test_update_page_order_applique_les_positions(self) -> None:
        page2 = Page.objects.create(name='Seconde', slug='seconde', order=1)
        response = self.client.post(
            reverse('update_page_order'),
            {'page': [page2.id, self.page.id]},
        )
        self.assertEqual(response.status_code, 200)
        page2.refresh_from_db()
        self.page.refresh_from_db()
        self.assertEqual(page2.order, 0)
        self.assertEqual(self.page.order, 1)


class SafeRefererTests(BaseTestCase):
    """#10 — _safe_referer empêche la redirection vers un domaine externe.

    Ces vues exigent désormais POST (@require_POST), d'où les self.client.post.
    """

    def test_referer_externe_redirige_vers_racine(self) -> None:
        widget = Widget.objects.create(
            title='Jetable', page=self.page, order=5, widget_type='list'
        )
        response = self.client.post(
            reverse('delete_widget', args=[widget.id]),
            HTTP_REFERER='http://evil.com/phishing',
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/')

    def test_referer_interne_est_conserve(self) -> None:
        response = self.client.post(
            reverse('toggle_widget_width', args=[self.widget.id]),
            HTTP_REFERER='/page/accueil/',
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/page/accueil/')


class HttpMethodTests(BaseTestCase):
    """Revue d'amélioration #1 — les vues mutatives refusent GET (405).

    Un GET mutatif est vulnérable au CSRF même derrière LoginRequiredMiddleware :
    les cookies SameSite=Lax partent avec une navigation GET de premier niveau,
    et la protection CSRF de Django ne couvre que les méthodes non sûres (POST).
    """

    def test_get_refuse_sur_les_vues_mutatives(self) -> None:
        link = Link.objects.create(
            title='Local', url='/tmp/fichier.txt', widget=self.widget, order=0
        )
        urls = [
            reverse('delete_link', args=[link.id]),
            reverse('delete_page', args=[self.page.id]),
            reverse('delete_widget', args=[self.widget.id]),
            reverse('toggle_widget_width', args=[self.widget.id]),
            reverse('open_local_file', args=[link.id]),
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 405)

    def test_get_sur_delete_ne_supprime_rien(self) -> None:
        """Le 405 doit être sans effet : l'objet survit au GET."""
        link = Link.objects.create(
            title='Survivant', url='https://exemple.com', widget=self.widget, order=0
        )
        self.client.get(reverse('delete_link', args=[link.id]))
        self.assertTrue(Link.objects.filter(id=link.id).exists())


class UniqueSlugTests(BaseTestCase):
    """Revue d'amélioration #6 — _unique_slug gère les collisions de slug."""

    def test_collision_ajoute_un_suffixe(self) -> None:
        # Le slug 'accueil' existe déjà (BaseTestCase) → suffixe -1 attendu.
        self.assertEqual(views._unique_slug('Accueil'), 'accueil-1')

    def test_sans_collision_retourne_le_slug_de_base(self) -> None:
        self.assertEqual(views._unique_slug('Projets Python'), 'projets-python')

    def test_renommage_conserve_son_propre_slug(self) -> None:
        # exclude_pk permet à une page de garder son slug lors du renommage.
        self.assertEqual(
            views._unique_slug('Accueil', exclude_pk=self.page.id), 'accueil'
        )


class NextOrderTests(BaseTestCase):
    """Revue d'amélioration #7 — next_order remplace le hack order=999."""

    def test_liste_vide_retourne_zero(self) -> None:
        self.assertEqual(next_order(self.widget.links), 0)

    def test_retourne_max_plus_un(self) -> None:
        Link.objects.create(title='A', url='a', widget=self.widget, order=4)
        self.assertEqual(next_order(self.widget.links), 5)

    def test_deux_ajouts_successifs_ont_des_ordres_distincts(self) -> None:
        """Via la vue add_widget : l'ancien hack donnait 999 aux deux."""
        for titre in ('W-a', 'W-b'):
            self.client.post(
                reverse('add_widget', args=[self.page.id]),
                {'title': titre, 'widget_type': 'list'},
            )
        wa = Widget.objects.get(title='W-a')
        wb = Widget.objects.get(title='W-b')
        self.assertNotEqual(wa.order, wb.order)


class PublicIpCacheTests(TestCase):
    """Revue d'amélioration #4 — cache TTL de l'IP publique.

    On teste le helper _get_public_ip directement, en simulant requests.get :
    aucun appel réseau réel n'est effectué.
    """

    def setUp(self) -> None:
        # Chaque test repart d'un cache vide (état module-level partagé).
        views._public_ip_cache.update(ip=None, expires=0.0)

    def test_le_cache_evite_les_appels_repetes(self) -> None:
        fake_response = Mock(text='203.0.113.7')
        with patch('dashboard.views.requests.get', return_value=fake_response) as mocked:
            self.assertEqual(views._get_public_ip(), '203.0.113.7')
            self.assertEqual(views._get_public_ip(), '203.0.113.7')
        # Deux lectures, mais une seule requête HTTP : le cache a servi.
        self.assertEqual(mocked.call_count, 1)

    def test_un_echec_reseau_n_est_pas_mis_en_cache(self) -> None:
        with patch(
            'dashboard.views.requests.get',
            side_effect=requests.RequestException,
        ) as mocked:
            self.assertEqual(views._get_public_ip(), 'Indisponible')
            self.assertEqual(views._get_public_ip(), 'Indisponible')
        # L'échec n'est pas caché : chaque lecture retente la requête.
        self.assertEqual(mocked.call_count, 2)
