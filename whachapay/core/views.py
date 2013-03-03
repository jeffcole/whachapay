import json, pprint, urllib
from datetime import date
from django.conf import settings
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.http import Http404, HttpResponse
from django.shortcuts import redirect, render_to_response
from django.template import RequestContext
from django.template.loader import render_to_string
from core import queries, util
from core.forms import HomeForm, EntryForm, TrimForm

_pp = pprint.PrettyPrinter(indent=2)
_rtr = render_to_response

### Views

def home(request):
    """
    Main home view.
    """
    # Check if the form has been submitted.
    if 'enter' in request.GET or 'find' in request.GET:
        form = HomeForm(request.GET)
        if form.is_valid():
            request.session['data'] = build_home_selection(form.cleaned_data)
            if 'enter' in request.GET:
                return redirect(dealer_select)
            else:
                return redirect(area_summary)
        else:
            # Reconstruct select options.
            build_vehicle_options(request.GET, form)
    else:
        form = HomeForm(initial={'make_year': 0})

    return _rtr('home/home.html', {'form': form},
                context_instance=RequestContext(request))

def build_home_selection(data):
    """
    Home view helper function. Build a dictionary of data for the downstream
    templates.
    """
    return {'vehicle': {'obj': {'make': data['make'], 
                                'model': data['model']},
                        'text': {'year': data['make_year'],
                                 'make_name':
                                     queries.get_make_name(data['make']),
                                 'model_name':
                                     queries.get_model_name(data['model'])},},
            'location': data['place_name'],
            'places': get_places(data['lat_lng'])}

def build_vehicle_options(get_data, form):
    """
    Home view helper function. Update the vehicle options on the form from the
    request GET data. Note that the form is being directly modified here.

    Nothing returned.
    """
    make_year = get_data.get('make_year', 0)
    make = get_data.get('make', 0)
    model = get_data.get('model', 0)

    form.fields['make'].choices = (
        [(m.id, m.name) for m in queries.get_make_options(make_year)])
    form.fields['make'].choices.insert(0, (0, 'Make'))
    form.fields['make'].initial = make

    form.fields['model'].choices = (
        [(m.id, m.name) for m in queries.get_model_options(make, make_year)])
    form.fields['model'].choices.insert(0, (0, 'Model'))
    form.fields['model'].initial = model

def ajax_home_update_selections(request):
    """
    Home screen vehicle selection Ajax view.

    Returns HttpResponse or raises Http404.
    """
    if request.is_ajax():
        # These might be 'Year', 'Make', or 'Model'.
        make_year = request.GET['make_year']
        make = request.GET['make']
        model = request.GET['model']
        selected = request.GET['selected']
        data = {}
        options = None

        if selected == 'make_year' and make_year.isdigit():
            options = queries.get_make_options(make_year)
        data['make'] = render_to_string('home/update_select.html',
                                        {'options': options,
                                         'name': 'Make'})
        options = None
        if selected == 'make' and make.isdigit():
            options = queries.get_model_options(make, make_year)
        data['model'] = render_to_string('home/update_select.html',
                                         {'options': options,
                                          'name': 'Model'})
        return HttpResponse(json.dumps(data), content_type='application/json')

    raise Http404

def dealer_select(request):
    """
    Dealer selection view.
    """
    if 'data' in request.session:
        data = request.session['data']
        # Set up pagination.
        places_results = ()
        if 'results' in data['places']:
            places_results = data['places']['results']
        results = get_page(request, places_results, 5)
        data['results'] = results
        # Make the places data available to JavaScript.
        data['places_json'] = json.dumps(results.object_list)
        request.session['data'] = data
        return _rtr('dealer_select.html', request.session['data'],
                    context_instance=RequestContext(request))
    raise Http404

def get_page(request, object_list, per_page):
    """
    Dealer select and area summary views helper function. Get the appropriate
    paginated subset of objects from a list.

    For an alternative that doesn't modify views, and uses the url rather than a
    GET param, see django-pagination:
    https://github.com/ericflo/django-pagination

    Returns Page.
    """
    paginator = Paginator(object_list, per_page)
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
    try:
        return paginator.page(page)
    except (EmptyPage, InvalidPage):
        return paginator.page(paginator.num_pages)

def deal_entry(request, place_id):
    """
    Deal entry view.
    """
    if 'data' in request.session:
        # Verify that the passed-in place is in the session.
        place_data = util.get_dict(
            request.session['data']['places']['results'], 'id', place_id)
        if not place_data:
            raise Http404
        data = {'vehicle': request.session['data']['vehicle'],
                'dealer': place_data}
        model_pk = data['vehicle']['obj']['model']
        trim_year = data['vehicle']['text']['year']
        data['place_json'] = json.dumps(place_data)
        if request.method == 'POST':
            form = EntryForm(request.POST, model_pk=model_pk, trim_year=trim_year,
                             label_suffix='')
            if form.is_valid():
                user_ip = queries.store_user_ip(request.META, form.cleaned_data)
                vehicle = queries.store_vehicle(data['vehicle'])
                dealer = queries.store_dealer(place_data)
                deal = queries.store_deal(user_ip, vehicle, dealer,
                                          form.cleaned_data)
                data['deal'] = deal
                request.session['data'] = data
                return redirect(deal_entered)
        else:
            form = EntryForm(initial={'date': date.today()}, model_pk=model_pk,
                             trim_year=trim_year, label_suffix='')
        data['form'] = form
    
        return _rtr('deal_entry.html', data,
                    context_instance=RequestContext(request))
    raise Http404

def deal_entered(request):
    """
    Deal entered confirmation view.
    """
    if 'data' in request.session:
        return _rtr('deal_entered.html', request.session['data'],
                    context_instance=RequestContext(request))
    raise Http404

def area_summary(request):
    """
    Area summary view.
    """
    if 'data' in request.session:
        data = request.session['data']
        # Get the vehicle instance from the database.
        v = data['vehicle']
        vehicle = queries.get_vehicle(v['text']['year'], v['obj']['make'],
                                      v['obj']['model'])
        # Get the trim to send to the deals query.
        form = TrimForm(request.GET, model_pk=v['obj']['model'],
                        trim_year=v['text']['year'])
        trim = None
        if 'trim' in request.GET and form.is_valid():
            trim = form.cleaned_data['trim']
        trim = trim if trim and int(trim) > 0 else None
        # Look up the dealers from the places.
        dealer_list, deal_count, area_avg = [], 0, 0
        places = ()
        if 'results' in data['places']:
            places = data['places']['results']
        for p in places:
            dealer = queries.get_dealer(p['id'])
            if dealer:
                # Look up the deals from the vehicle and dealer instances.
                deals = queries.get_deals(vehicle, dealer, trim)
                deal_count += len(deals)
                dealer_sum = get_deals_sum(deals)
                area_avg += dealer_sum
                # Add dealer and average to data if deals were found.
                if deals:
                    dealer_avg = dealer_sum / len(deals)
                    dealer_list.append({'obj': dealer, 'avg': dealer_avg})
        # Set up pagination.
        dealers = get_page(request, dealer_list, 5)
        places_for_js = [{'location': d['obj'].location,
                          'id': d['obj'].place_id,
                          'name': d['obj'].name}
                         for d in dealers.object_list]
        # Set up template variables.
        data['area_avg'] = area_avg / (deal_count if deal_count > 0 else 1)
        data['dealers'] = dealers
        data['form'] = form
        data['form_action'] = 'area_summary'
        data['trim'] = trim
        data['places_json'] = json.dumps(places_for_js)
        request.session['data'] = data
        return _rtr('area_summary.html', request.session['data'],
                    context_instance=RequestContext(request))
    raise Http404

def get_deals_sum(deals):
    """
    Area summary and dealer deals views helper function. Sum the prices of
    a list of deals.
    
    Returns int.
    """
    deals_sum = 0
    for d in deals:
        deals_sum += d.price
    return deals_sum

def dealer_deals(request, place_id):
    """
    Dealer deals view.
    """
    dealer = queries.get_dealer(place_id)
    if 'data' in request.session and dealer:
        data = request.session['data']
        # Get the vehicle instance from the database.
        v = data['vehicle']
        vehicle = queries.get_vehicle(v['text']['year'], v['obj']['make'],
                                      v['obj']['model'])
        if not vehicle:
            raise Http404
        # Get the trim to send to the deals query.
        trim = None
        #  Try for the trim specified in the form.
        form = TrimForm(request.GET, model_pk=v['obj']['model'],
                        trim_year=v['text']['year'])
        # Fall back on the trim specified in the session.
        if 'trim' not in request.GET and 'trim' in data:
            form = TrimForm(data, model_pk=v['obj']['model'],
                            trim_year=v['text']['year'])
        if form.is_valid():
            trim = form.cleaned_data['trim']
        trim = trim if trim and int(trim) > 0 else None
        # Look up the deals from the vehicle and dealer instances.
        deals = queries.get_deals(vehicle, dealer, trim)
        data['dealer'] = dealer
        data['deals'] = deals
        data['dealer_avg'] = get_deals_sum(deals) / (len(deals) if len(deals) > 0
                                                     else 1)
        data['form'] = form
        data['form_action'] = 'dealer_deals'
        place_data = util.get_dict(data['places']['results'], 'id', place_id)
        data['place_json'] = json.dumps(place_data)
        request.session['data'] = data
        return _rtr('dealer_deals.html', request.session['data'],
                    context_instance=RequestContext(request))
    raise Http404

def deal_detail(request, deal_pk):
    """
    Deal detail view.
    """
    deal = queries.get_deal(deal_pk)
    if 'data' in request.session and deal:
        data = request.session['data']
        data['deal'] = deal
        # Clear the form action so that the trim filter isn't rendered.
        if 'form_action' in data:
            del data['form_action']
        request.session['data'] = data
        return _rtr('deal_detail.html', request.session['data'],
                    context_instance=RequestContext(request))
    raise Http404
    
### Google Maps API web service calls

def get_places(location):
    """
    Make a request to the Google Places API with the given location,
    radius (in meters), GPS sensor, keyword, and types.

    Returns dictionary.
    """
    geo_args = {'key': settings.GMAP_API_KEY,
                'location': location,
                'radius': '50000',
                'sensor': 'false',
                'keyword': 'car+dealer',
                'types': 'car_dealer|establishment'}
    url = settings.GMAP_PLACE_URL + '?' + urllib.urlencode(geo_args)
    response = None
    try:
        usock = urllib.urlopen(url)
        try:
            response = json.load(usock)
        finally:
            usock.close()
    except IOError:
        pass
    try:
        if response and response['status'] == 'OK':
            return build_places(response)
    except KeyError:
        pass
    return {}
    
def build_places(response):
    """
    get_places helper function. Construct a dictionary of just the relevant
    places data.
    
    Returns dictionary:
        { 'results': [ { 'location': '',
                         'id': '',
                         'name': '',
                         'vicinity': ''}]
          'html_attributions': []}
    """
    results = [{'location': str(r['geometry']['location']['lat']) + ','
                + str(r['geometry']['location']['lng']),
                'id': r['id'],
                'name': r['name'],
                'vicinity': r['vicinity'] } for r in response['results']]
    places = {'html_attributions': response['html_attributions']}
    places['results'] = results
    return places
