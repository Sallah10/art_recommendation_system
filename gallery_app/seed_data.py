"""
Demo catalogue used by `python manage.py seed_gallery`.

The images in `static/img` are public-domain artwork scans that shipped with the
original project. Artist attribution was not part of the source data, so most
records are marked "Unattributed" rather than guessing. Style and period labels
are illustrative demo metadata - edit this file (or the Django admin) with your
own catalogue data.
"""

DEFAULT_DESCRIPTION = (
    "A study in composition, colour and light from the EsCurator demo archive. "
    "The work rewards a slow look: notice how the eye is guided across the frame."
)

# filename: (title, style, era, medium, description)
CATALOG = {
    "actor.jpg": ("The Actor", "Portrait", "Historical", "Oil on canvas", "A theatrical portrait built on a single, confident line of profile."),
    "alpha.jpg": ("Alpha", "Abstract", "Modern", "Mixed media", "An exercise in rhythm and negative space rather than representation."),
    "ann_in.jpg": ("Ann in Repose", "Portrait", "Historical", "Oil on canvas", "A quiet seated portrait; the sitter's hands do as much storytelling as the face."),
    "at_the_shore.jpg": ("At the Shore", "Landscape", "Historical", "Oil on canvas", "Foam, horizon and weather - a coastal scene that is mostly atmosphere."),
    "battle_of_naked_men.jpg": ("Battle of Naked Men", "Figure Study", "Historical", "Engraving", "A dense tangle of bodies that turns anatomy into a pattern of movement."),
    "border.jpg": ("The Border", "Landscape", "Historical", "Oil on canvas", "A restrained landscape where the horizon carries almost all of the weight."),
    "broken_land.jpg": ("Broken Land", "Landscape", "Pre-1900", "Oil on canvas", "Furrowed ground and a low sky; the palette stays close to earth and ash."),
    "bungo_province.jpg": ("Bungo Province", "Landscape", "Edo period", "Woodblock print", "One of a series of provincial views, all steep slopes and drifting mist."),
    "chicago.jpg": ("Chicago", "Cityscape", "20th century", "Oil on canvas", "An urban view flattened into planes of smoke, stone and water."),
    "city.jpg": ("The City", "Cityscape", "Modern", "Oil on canvas", "Buildings reduced to geometry; the streets read like brushstrokes."),
    "cooling_off.jpg": ("Cooling Off", "Genre Scene", "Historical", "Oil on canvas", "A candid moment of rest, painted with warm, unfussy light."),
    "cover_with.jpg": ("Cover With", "Textile", "Historical", "Textile", "A patterned cover study - repeat, symmetry and hand-made irregularity."),
    "crossing_the_frozen.jpg": ("Crossing the Frozen", "Landscape", "Historical", "Oil on canvas", "Figures crossing a winter expanse; scale is everything here."),
    "falcon.jpg": ("The Falcon", "Animal Study", "Historical", "Oil on panel", "A bird of prey held mid-gesture, all tension and feather."),
    "female_nude.jpg": ("Female Nude", "Figure Study", "Historical", "Oil on canvas", "A classical figure study concerned with posture rather than narrative."),
    "fgures in interior.jpg": ("Figures in an Interior", "Genre Scene", "Historical", "Oil on canvas", "Domestic life staged in a shallow, luminous room."),
    "for_london_music.jpg": ("For London Music", "Poster", "Modern", "Lithograph", "A graphic poster that treats type and image as a single composition."),
    "goat_carts.jpg": ("Goat Carts", "Genre Scene", "Historical", "Oil on canvas", "Everyday labour on the move, painted with a documentary eye."),
    "goddess.jpg": ("Goddess", "Portrait", "Historical", "Oil on canvas", "An idealised figure framed by attributes rather than a setting."),
    "god_the_father.jpg": ("God the Father", "Religious", "Historical", "Tempera on panel", "A devotional image built around gesture, gold and upward gaze."),
    "group.jpg": ("The Group", "Portrait", "Historical", "Oil on canvas", "A group portrait where the arrangement tells you who matters."),
    "harima_province.jpg": ("Harima Province", "Landscape", "Edo period", "Woodblock print", "A provincial view from a print series; bold line and flat colour."),
    "headcloth.jpg": ("Headcloth", "Textile", "Historical", "Textile", "A close study of weave, dye and the geometry of folded cloth."),
    "headcloth_indo.jpg": ("Headcloth, Indonesia", "Textile", "Historical", "Textile", "An Indonesian headcloth study with a dense, repeating motif."),
    "headdress.jpg": ("Headdress", "Textile", "Historical", "Mixed media", "Ornament as portrait: the object carries the presence."),
    "iket.jpg": ("Ikat", "Textile", "Historical", "Textile", "The blurred edges of ikat dyeing become the subject itself."),
    "juvisy_france.jpg": ("Juvisy, France", "Landscape", "19th century", "Oil on canvas", "A French town seen from a distance, softened by haze."),
    "kastro.jpg": ("Kastro", "Landscape", "Historical", "Oil on canvas", "Whitewashed walls and hard Mediterranean light."),
    "landscape_with.jpg": ("Landscape With", "Landscape", "Historical", "Oil on canvas", "A classical landscape with a small human incident for scale."),
    "les_anglais.jpg": ("Les Anglais", "Genre Scene", "Historical", "Oil on canvas", "A social scene observed with gentle, satirical distance."),
    "les_invalides.jpg": ("Les Invalides", "Cityscape", "19th century", "Oil on canvas", "Monumental architecture painted as weather and light."),
    "melon_shaped.jpg": ("Melon Shaped", "Still Life", "Historical", "Oil on canvas", "A still life that is really a study of surface and curve."),
    "murder.jpg": ("Murder", "Narrative", "Historical", "Oil on canvas", "A dramatic narrative scene staged for maximum tension."),
    "musashi_province.jpg": ("Musashi Province", "Landscape", "Edo period", "Woodblock print", "A provincial view with a strong diagonal of land and water."),
    "on_a_balcony.jpg": ("On a Balcony", "Genre Scene", "19th century", "Oil on canvas", "A figure at a balcony, half in sunlight, half in shadow."),
    "ornament.jpg": ("Ornament", "Design Study", "Historical", "Mixed media", "A pattern study that treats decoration as its own visual language."),
    "panel.jpg": ("Panel", "Design Study", "Historical", "Tempera on panel", "A panel study of colour blocking and simple geometry."),
    "pentaptych.jpg": ("Pentaptych", "Religious", "Historical", "Tempera on panel", "A multi-panel work whose structure shapes how it is read."),
    "praying_jew.jpg": ("Praying Jew", "Portrait", "Historical", "Oil on canvas", "A portrait of devotion, held in a narrow, intimate frame."),
    "self_portrait.jpg": ("Self Portrait", "Portrait", "Historical", "Oil on canvas", "The artist turns the same scrutiny on themself that they give a sitter."),
    "shawl.jpg": ("Shawl", "Textile", "Historical", "Textile", "Drapery as subject: folds, fringe and a long fall of colour."),
    "still_life.jpg": ("Still Life", "Still Life", "Historical", "Oil on canvas", "Objects arranged for light, not for use."),
    "the_baby_in.jpg": ("The Baby In", "Genre Scene", "Historical", "Oil on canvas", "A domestic interior centred on the smallest figure in the room."),
    "the_bath.jpg": ("The Bath", "Figure Study", "Historical", "Oil on canvas", "Water, skin and reflected light handled with great restraint."),
    "the_beach_at.jpg": ("The Beach At", "Landscape", "19th century", "Oil on canvas", "A beach at low tide; most of the painting is sky."),
    "the_circumcision.jpg": ("The Circumcision", "Religious", "Historical", "Tempera on panel", "A devotional scene compressed into a tight architectural space."),
    "the_day_after.jpg": ("The Day After", "Narrative", "Historical", "Oil on canvas", "A narrative image that withholds its story just long enough."),
    "the_presentation.jpg": ("The Presentation", "Religious", "Historical", "Tempera on panel", "A ceremonial scene built on a strong central axis."),
    "three_children.jpg": ("Three Children", "Portrait", "Historical", "Oil on canvas", "Three sitters, three moods, one shared light source."),
    "tingle_tangle.jpg": ("Tingle Tangle", "Abstract", "Modern", "Mixed media", "Playful, dense mark-making that refuses a single focal point."),
    "trapeze_artiste.jpg": ("Trapeze Artiste", "Poster", "Modern", "Lithograph", "A performance poster that sells motion before it sells the event."),
    "untitled.jpg": ("Untitled", "Abstract", "Modern", "Mixed media", "An untitled study - the title would only get in the way."),
    "vessel_depicting.jpg": ("Vessel Depicting", "Decorative Arts", "Historical", "Ceramic", "A vessel whose surface carries its own narrative frieze."),
    "waiting.jpg": ("Waiting", "Portrait", "Historical", "Oil on canvas", "Stillness as a subject; almost nothing happens, beautifully."),
    "waiting_.jpg": ("Waiting II", "Figure Study", "Historical", "Oil on canvas", "A companion study to Waiting, with a softer, closer crop."),
}

# Curated shelves. Slugs are generated from the names.
COLLECTIONS = [
    {
        "name": "Quiet Landscapes",
        "description": "Horizons, weather and the places where the eye can rest.",
        "accent": "#6B7A5E",
        "featured": True,
        "styles": ["Landscape", "Cityscape"],
    },
    {
        "name": "Faces & Figures",
        "description": "Portraits and figure studies that reward a second look.",
        "accent": "#C4532D",
        "featured": True,
        "styles": ["Portrait", "Figure Study"],
    },
    {
        "name": "Textile & Ornament",
        "description": "Pattern, weave and decoration treated as fine art.",
        "accent": "#B08442",
        "featured": True,
        "styles": ["Textile", "Design Study", "Decorative Arts"],
    },
    {
        "name": "Modern Experiments",
        "description": "Abstraction, posters and work that breaks the frame.",
        "accent": "#4C5B7A",
        "featured": False,
        "styles": ["Abstract", "Poster", "Modern"],
    },
    {
        "name": "Stories & Devotion",
        "description": "Narrative, religious and genre scenes with something to say.",
        "accent": "#7A4C5B",
        "featured": False,
        "styles": ["Narrative", "Religious", "Genre Scene"],
    },
]

FEATURED_FILENAMES = {
    "self_portrait.jpg",
    "harima_province.jpg",
    "still_life.jpg",
    "the_bath.jpg",
    "at_the_shore.jpg",
    "three_children.jpg",
}
