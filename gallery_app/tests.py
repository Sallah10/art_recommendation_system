from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase

from .models import Art_Work, Collection, UserInteraction
from .recommendations import recommend_for_session, similar_artworks

SESSION = "test-session-0001"


def make_artwork(title, style="Landscape", era="Historical", medium="Oil on canvas"):
    return Art_Work.objects.create(
        art_title=title,
        artiste="Unattributed",
        style=style,
        era=era,
        medium=medium,
        art_desc=f"{title} description",
    )


class CatalogueApiTests(APITestCase):
    def setUp(self):
        self.shore = make_artwork("At the Shore")
        self.border = make_artwork("The Border")
        self.portrait = make_artwork("The Actor", style="Portrait")
        self.collection = Collection.objects.create(
            name="Quiet Landscapes", description="Landscapes"
        )
        self.collection.artworks.set([self.shore, self.border])

    def test_health(self):
        response = self.client.get("/api/health/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], "ok")

    def test_cors_preflight_allows_session_header(self):
        response = self.client.options(
            "/api/art_works/",
            HTTP_ORIGIN="http://localhost:5173",
            HTTP_ACCESS_CONTROL_REQUEST_METHOD="GET",
            HTTP_ACCESS_CONTROL_REQUEST_HEADERS="x-session-id",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response["Access-Control-Allow-Origin"], "http://localhost:5173"
        )
        self.assertIn("x-session-id", response["Access-Control-Allow-Headers"])

    def test_artwork_list_is_paginated(self):
        response = self.client.get("/api/art_works/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("results", response.data)
        self.assertEqual(response.data["count"], 3)

    def test_seeded_artwork_images_use_collected_static_assets(self):
        for filename, expected_url in (
            ("at_the_shore.jpg", "/static/img/at_the_shore.jpg"),
            ("fgures in interior.jpg", "/static/img/fgures%20in%20interior.jpg"),
        ):
            with self.subTest(filename=filename):
                self.shore.art_image = f"artworks/{filename}"
                self.shore.save(update_fields=["art_image"])

                response = self.client.get(f"/api/art_works/{self.shore.id}/")

                self.assertEqual(response.status_code, 200)
                self.assertTrue(response.data["art_image"].endswith(expected_url))

    def test_filter_by_style_and_search(self):
        response = self.client.get("/api/art_works/?style=Portrait")
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["art_title"], "The Actor")

        response = self.client.get("/api/art_works/?search=shore")
        self.assertEqual(response.data["count"], 1)

    def test_collection_detail_includes_artwork_count(self):
        response = self.client.get("/api/collections/quiet-landscapes/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["artwork_count"], 2)

    def test_similar_returns_same_style(self):
        response = self.client.get(f"/api/art_works/{self.shore.id}/similar/")
        self.assertEqual(response.status_code, 200)
        titles = [item["art_title"] for item in response.data]
        self.assertIn("The Border", titles)

    def test_stats(self):
        response = self.client.get("/api/stats/")
        self.assertEqual(response.data["artworks"], 3)
        self.assertEqual(response.data["collections"], 1)


class InteractionApiTests(APITestCase):
    def setUp(self):
        self.artwork = make_artwork("At the Shore")

    def post_interaction(self, kind, session=SESSION):
        return self.client.post(
            "/api/interactions/",
            {"artwork": self.artwork.id, "type": kind},
            HTTP_X_SESSION_ID=session,
        )

    def test_session_is_required(self):
        response = self.client.post(
            "/api/interactions/", {"artwork": self.artwork.id, "type": "like"}
        )
        self.assertEqual(response.status_code, 400)

    def test_like_toggles_and_counts(self):
        response = self.post_interaction("like")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["liked"])
        self.assertEqual(response.data["likes"], 1)

        response = self.post_interaction("like")
        self.assertFalse(response.data["liked"])
        self.assertEqual(response.data["likes"], 0)

    def test_bookmark_and_view(self):
        self.post_interaction("bookmark")
        response = self.post_interaction("view")
        self.assertTrue(response.data["bookmarked"])
        self.assertEqual(response.data["view_count"], 1)

    def test_invalid_type_is_rejected(self):
        response = self.post_interaction("love")
        self.assertEqual(response.status_code, 400)

    def test_interactions_are_scoped_to_session(self):
        self.post_interaction("like")
        other = self.client.get(
            "/api/interactions/", HTTP_X_SESSION_ID="other-session-9999"
        )
        self.assertEqual(len(other.data), 0)

    def test_artwork_list_reflects_session_state(self):
        self.post_interaction("like")
        self.post_interaction("bookmark")
        response = self.client.get("/api/art_works/", HTTP_X_SESSION_ID=SESSION)
        item = response.data["results"][0]
        self.assertTrue(item["is_liked"])
        self.assertTrue(item["is_bookmarked"])


class RecommendationTests(APITestCase):
    def setUp(self):
        self.shore = make_artwork("At the Shore")
        self.border = make_artwork("The Border")
        self.beach = make_artwork("The Beach At")
        self.portrait = make_artwork("The Actor", style="Portrait")

    def test_cold_start_returns_results(self):
        response = self.client.post("/api/recommendations/", {"limit": 2})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 2)

    def test_personalised_recommendation_prefers_similar_style(self):
        UserInteraction.objects.create(
            session_key=SESSION, artwork=self.shore, liked=True
        )
        response = self.client.post(
            "/api/recommendations/",
            {"limit": 2},
            HTTP_X_SESSION_ID=SESSION,
        )
        self.assertEqual(response.status_code, 200)
        titles = [item["art_title"] for item in response.data["results"]]
        self.assertIn("The Border", titles)
        self.assertNotIn("At the Shore", titles)
        self.assertTrue(response.data["results"][0]["reason"])

    def test_engine_excludes_liked_items(self):
        UserInteraction.objects.create(
            session_key=SESSION, artwork=self.shore, liked=True
        )
        ranked = recommend_for_session(SESSION, limit=10)
        ids = [item["artwork"].id for item in ranked]
        self.assertNotIn(self.shore.id, ids)

    def test_similar_artworks_ignores_unrelated(self):
        neighbours = similar_artworks(self.portrait, limit=4)
        self.assertIsInstance(neighbours, list)

    def test_taste_profile(self):
        UserInteraction.objects.create(
            session_key=SESSION, artwork=self.shore, liked=True
        )
        response = self.client.get("/api/taste/", HTTP_X_SESSION_ID=SESSION)
        self.assertEqual(response.data["signals"], 1)
        self.assertEqual(response.data["top_styles"], ["Landscape"])


class AuthApiTests(APITestCase):
    def test_register_login_me_logout(self):
        response = self.client.post(
            "/api/auth/register/",
            {"name": "Ada", "email": "ada@example.com", "password": "S3cure-pass-123"},
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["email"], "ada@example.com")
        self.assertTrue(User.objects.filter(email="ada@example.com").exists())

        me = self.client.get("/api/auth/me/")
        self.assertEqual(me.status_code, 200)

        logout = self.client.post("/api/auth/logout/")
        self.assertEqual(logout.status_code, 200)

        login = self.client.post(
            "/api/auth/login/",
            {"email": "ada@example.com", "password": "S3cure-pass-123"},
        )
        self.assertEqual(login.status_code, 200)

    def test_duplicate_email_is_rejected(self):
        User.objects.create_user(
            username="existing@example.com",
            email="existing@example.com",
            password="S3cure-pass-123",
        )
        response = self.client.post(
            "/api/auth/register/",
            {"email": "existing@example.com", "password": "S3cure-pass-123"},
        )
        self.assertEqual(response.status_code, 400)
