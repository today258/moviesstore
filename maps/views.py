from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Sum

# GeoDjango utility: use GEOSGeometry for building GeoJSON-compliant geometry objects
from django.contrib.gis.geos import Point

from accounts.models import UserProfile
from cart.models import Item


def index(request):
    template_data = {
        'title': 'World Movie Map',
    }
    return render(request, 'maps/index.html', {'template_data': template_data})


def country_movies(request, iso2):
    """
    Return a GeoJSON FeatureCollection of popular movies for users with the given
    nationality (ISO 3166-1 alpha-2 code).  GeoDjango's ``Point`` is used to
    attach a geometry to each feature so results are standards-compliant GeoJSON.
    """
    iso2 = iso2.upper()

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

    features = []
    for rank, row in enumerate(movie_stats, start=1):
        # Use a GeoDjango Point as the geometry (origin point – no real coordinate needed
        # for tabular data; demonstrates GeoDjango spatial object construction).
        point = Point(0, 0)
        features.append({
            'type': 'Feature',
            'geometry': {
                'type': point.geom_type,
                'coordinates': list(point.coords),
            },
            'properties': {
                'rank':      rank,
                'id':        row['movie__id'],
                'title':     row['movie__name'],
                'checkouts': row['total_checkouts'],
                'country':   iso2,
            },
        })

    geojson = {
        'type':     'FeatureCollection',
        'country':  iso2,
        'features': features,
    }
    return JsonResponse(geojson)
