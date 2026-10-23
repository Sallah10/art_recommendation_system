"""
A small, explainable hybrid recommender.

No model file, no GPU, no training step: it combines three signals that the
database already knows how to produce.

1. Content  - how much a candidate shares style/era/medium/artist with what the
              visitor already engaged with.
2. Collaborative - what visitors with similar taste engaged with.
3. Popularity - a gentle cold-start fallback and tie breaker.

Every recommendation carries a human-readable `reason`, which is what makes the
"For you" shelf feel like a product instead of a black box.
"""

from collections import Counter, defaultdict

from django.conf import settings
from django.db.models import Count, Q, Sum

from .models import Art_Work, UserInteraction


def _weights():
    config = getattr(settings, "RECOMMENDATION_WEIGHTS", {})
    return (
        config.get("like", 3.0),
        config.get("bookmark", 2.5),
        config.get("view", 0.2),
    )


def _tagset(artwork):
    tags = {tag.strip().lower() for tag in artwork.tags if tag}
    if artwork.artiste and artwork.artiste.lower() != "unattributed":
        tags.add(artwork.artiste.lower())
    return tags


def _jaccard(left, right):
    if not left or not right:
        return 0.0
    union = left | right
    return len(left & right) / len(union)


def _interaction_weight(interaction, like_weight, bookmark_weight, view_weight):
    weight = 0.0
    if interaction.liked:
        weight += like_weight
    if interaction.bookmarked:
        weight += bookmark_weight
    weight += min(interaction.view_count, 10) * view_weight
    return weight


def _content_scores(artworks, interactions, like_weight, bookmark_weight, view_weight):
    """Return {artwork_id: (score, strongest_source_artwork)}."""
    profile = []
    for interaction in interactions:
        weight = _interaction_weight(
            interaction, like_weight, bookmark_weight, view_weight
        )
        if weight > 0:
            profile.append((interaction.artwork_id, weight))

    if not profile:
        return {}, {}

    total_weight = sum(weight for _, weight in profile)
    tag_cache = {artwork.id: _tagset(artwork) for artwork in artworks}
    lookup = {artwork.id: artwork for artwork in artworks}
    scores = defaultdict(float)
    reasons = {}

    for artwork in artworks:
        candidate_tags = tag_cache[artwork.id]
        for source_id, weight in profile:
            source = lookup.get(source_id)
            if source is None:
                continue
            similarity = _jaccard(candidate_tags, tag_cache[source.id])
            if similarity <= 0:
                continue
            contribution = similarity * (weight / total_weight)
            scores[artwork.id] += contribution
            current = reasons.get(artwork.id)
            if current is None or contribution > current[0]:
                reasons[artwork.id] = (contribution, source.art_title)

    return dict(scores), {key: value[1] for key, value in reasons.items()}


def _collaborative_scores(interactions):
    """Sessions that liked what this visitor liked also engaged with..."""
    liked_ids = [interaction.artwork_id for interaction in interactions if interaction.liked]
    if not liked_ids:
        return {}, {}

    neighbour_sessions = (
        UserInteraction.objects.filter(artwork_id__in=liked_ids, liked=True)
        .exclude(session_key="")
        .values_list("session_key", flat=True)
        .distinct()
    )

    counts = (
        UserInteraction.objects.filter(
            session_key__in=neighbour_sessions
        )
        .filter(Q(liked=True) | Q(bookmarked=True))
        .values("artwork_id")
        .annotate(score=Count("id"))
        .order_by("-score")
    )

    scores = {}
    for row in counts:
        if row["artwork_id"] in liked_ids:
            continue
        scores[row["artwork_id"]] = float(row["score"])

    best = max(scores.values()) if scores else 0.0
    if best:
        scores = {key: value / best for key, value in scores.items()}
    return scores, {}


def _popularity_scores(artworks):
    raw = {}
    for artwork in artworks:
        likes = getattr(artwork, "likes", 0) or 0
        bookmarks = getattr(artwork, "bookmarks", 0) or 0
        views = getattr(artwork, "views", 0) or 0
        raw[artwork.id] = float(likes) * 3 + float(bookmarks) * 2 + float(views) * 0.1

    best = max(raw.values()) if raw else 0.0
    if best:
        raw = {key: value / best for key, value in raw.items()}
    return raw


def _reason(artwork, content_reason, collaborative, popularity, has_profile):
    if content_reason:
        return f"Because you liked {content_reason}"
    if collaborative > 0:
        return "Popular with visitors who share your taste"
    if artwork.style:
        return f"Trending in {artwork.style}"
    if artwork.featured:
        return "A curator's pick"
    if not has_profile:
        return "A good place to start"
    return "More to explore"


def recommend_for_session(session_key, limit=8):
    """Return a ranked list of dicts ready for RecommendedArtWorkSerializer."""
    like_weight, bookmark_weight, view_weight = _weights()

    artworks = list(
        Art_Work.objects.annotate(
            likes=Count("interactions", filter=Q(interactions__liked=True)),
            bookmarks=Count("interactions", filter=Q(interactions__bookmarked=True)),
            views=Sum("interactions__view_count"),
        )
    )
    if not artworks:
        return []

    interactions = list(
        UserInteraction.objects.filter(session_key=session_key).select_related("artwork")
    )
    positive_ids = {
        interaction.artwork_id
        for interaction in interactions
        if interaction.liked or interaction.bookmarked
    }

    content, content_reasons = _content_scores(
        artworks, interactions, like_weight, bookmark_weight, view_weight
    )
    collaborative, _ = _collaborative_scores(interactions)
    popularity = _popularity_scores(artworks)

    has_profile = bool(content) or bool(collaborative)
    if has_profile:
        weights = (0.55, 0.25, 0.20)
    else:
        weights = (0.0, 0.0, 1.0)

    ranked = []
    for artwork in artworks:
        if artwork.id in positive_ids:
            continue
        content_score = content.get(artwork.id, 0.0)
        collaborative_score = collaborative.get(artwork.id, 0.0)
        popularity_score = popularity.get(artwork.id, 0.0)
        score = (
            weights[0] * content_score
            + weights[1] * collaborative_score
            + weights[2] * popularity_score
        )
        if not has_profile and artwork.featured:
            score += 0.35
        ranked.append(
            {
                "artwork": artwork,
                "score": round(score, 4),
                "reason": _reason(
                    artwork,
                    content_reasons.get(artwork.id),
                    collaborative_score,
                    popularity_score,
                    has_profile,
                ),
            }
        )

    ranked.sort(key=lambda item: (-item["score"], item["artwork"].art_title))
    return ranked[:limit]


def similar_artworks(artwork, limit=4):
    """Content-only neighbours, used on the artwork detail page."""
    candidates = list(
        Art_Work.objects.exclude(id=artwork.id).annotate(
            likes=Count("interactions", filter=Q(interactions__liked=True)),
            bookmarks=Count("interactions", filter=Q(interactions__bookmarked=True)),
            views=Sum("interactions__view_count"),
        )
    )
    source_tags = _tagset(artwork)
    if not source_tags:
        return []
    scored = []
    for candidate in candidates:
        overlap = _jaccard(source_tags, _tagset(candidate))
        if overlap <= 0:
            continue
        scored.append((overlap, candidate))
    scored.sort(key=lambda item: (-item[0], item[1].art_title))
    return [candidate for _, candidate in scored[:limit]]


def interaction_map_for_session(session_key):
    if not session_key:
        return {}
    rows = UserInteraction.objects.filter(session_key=session_key).values(
        "artwork_id", "liked", "bookmarked"
    )
    return {
        row["artwork_id"]: {"liked": row["liked"], "bookmarked": row["bookmarked"]}
        for row in rows
    }


def taste_profile(session_key):
    """A small summary the UI can display: favourite styles and counts."""
    interactions = UserInteraction.objects.filter(session_key=session_key)
    if not interactions.exists():
        return {"signals": 0, "top_styles": [], "top_eras": []}

    artwork_ids = [row["artwork_id"] for row in interactions.values("artwork_id")]
    artworks = Art_Work.objects.filter(id__in=artwork_ids)
    styles = Counter(a.style for a in artworks if a.style)
    eras = Counter(a.era for a in artworks if a.era)
    return {
        "signals": interactions.count(),
        "top_styles": [name for name, _ in styles.most_common(3)],
        "top_eras": [name for name, _ in eras.most_common(3)],
    }
