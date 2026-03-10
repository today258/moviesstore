from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Sum
import pycountry

from accounts.models import UserProfile
from cart.models import Item


def _resolve_iso2(code):
    """
    Accept an ISO 3166-1 alpha-2, alpha-3, or country name and return the
    canonical 2-letter code, or None if unresolvable.
    """
    code = (code or '').strip()
    if not code:
        return None
    if len(code) == 2:
        c = pycountry.countries.get(alpha_2=code.upper())
        return c.alpha_2 if c else None
    if len(code) == 3:
        c = pycountry.countries.get(alpha_3=code.upper())
        return c.alpha_2 if c else None
    # Try fuzzy name search
    try:
        results = pycountry.countries.search_fuzzy(code)
        return results[0].alpha_2 if results else None
    except LookupError:
        return None


def index(request):
    template_data = {
        'title': 'World Movie Map',
    }
    return render(request, 'maps/index.html', {'template_data': template_data})


def country_movies(request, code):
    """
    Return a GeoJSON FeatureCollection of the top movies purchased by users
    from a given country. ``code`` can be an ISO 3166-1 alpha-2 code,
    alpha-3 code, or country name — all are normalised to alpha-2 via pycountry.
    """
    iso2 = _resolve_iso2(code)
    if not iso2:
        return JsonResponse({'error': f'Unknown country code: {code}'}, status=404)

    user_ids = UserProfile.objects.filter(
        nationality=iso2
    ).values_list('user_id', flat=True)

    movie_stats = (
        Item.objects
        .filter(order__user_id__in=user_ids)
        .values('movie__id', 'movie__name')
        .annotate(total_checkouts=Sum('quantity'))
        .order_by('-total_checkouts')[:10]
    )

    features = [
        {
            'type': 'Feature',
            'geometry': None,
            'properties': {
                'rank':      rank,
                'id':        row['movie__id'],
                'title':     row['movie__name'],
                'checkouts': row['total_checkouts'],
                'country':   iso2,
            },
        }
        for rank, row in enumerate(movie_stats, start=1)
    ]

    return JsonResponse({
        'type':     'FeatureCollection',
        'country':  iso2,
        'features': features,
    })

