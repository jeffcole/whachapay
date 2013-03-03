from core import util
from core.models import (Deal, Dealer, IPAddress, Make, MakeYear, Model, Trim,
                         User, UserIP, Vehicle)

def get_make_options(make_year):
    """Get all makes for a given year."""
    return Make.objects.filter(makeyear__year__exact=make_year)

def get_model_options(make_pk, model_year):
    """Get all models for a given make and year."""
    return Model.objects.filter(make=make_pk).filter(
        modelyear__year__exact=model_year)

def get_trim_options(model_pk, trim_year):
    """Get all trims for a given model and year."""
    return Trim.objects.filter(model=model_pk).filter(
        trimyear__year__exact=trim_year)

def get_make_name(make_pk):
    """Get a make name for a given pk."""
    return Make.objects.filter(pk=make_pk).values_list('name', flat=True)[0]

def get_model_name(model_pk):
    """Get a model name for a given pk."""
    return Model.objects.filter(pk=model_pk).values_list('name', flat=True)[0]

def get_trim_name(trim_pk):
    """Get a trim name for a given pk."""
    return Trim.objects.filter(pk=trim_pk).values_list('name', flat=True)[0]

def get_make_year(make_pk, make_year):
    """Get a make year for a given make pk and year."""
    return MakeYear.objects.get(make=make_pk, year=make_year)

def get_make(make_pk):
    """Get a make for a given pk."""
    return Make.objects.get(pk=make_pk)

def get_model(model_pk):
    """Get a model for a given pk."""
    return Model.objects.get(pk=model_pk)

def get_trim(trim_pk):
    """Get a trim for a given pk."""
    return Trim.objects.get(pk=trim_pk)

def get_vehicle(make_year, make_pk, model_pk):
    """Get a vehicle for the given params."""
    try:
        return Vehicle.objects.get(make_year=get_make_year(make_pk, make_year),
                                   make=make_pk, model=model_pk)
    except Vehicle.DoesNotExist:
        return None

def get_dealer(place_id):
    """Get a dealer for a given place id."""
    try:
        return Dealer.objects.get(place_id=place_id)
    except Dealer.DoesNotExist:
        return None

def get_deals(vehicle, dealer, trim):
    """
    Get the deals for a given vehicle, dealer, and optional trim.

    Returns list, empty if none found.
    """
    deals = Deal.objects.filter(vehicle=vehicle, dealer=dealer)
    return deals.filter(trim=trim) if trim else deals

def get_deal(deal_pk):
    """Get a deal for a given pk."""
    try:
        return Deal.objects.get(pk=deal_pk)
    except Deal.DoesNotExist:
        return None

def store_user_ip(meta, form_data):
    """
    Deal entry view helper function.

    Returns UserIP.
    """
    ip, ipcreated = IPAddress.objects.get_or_create(
        ip=util.get_client_ip(meta))
    user, usercreated = User.objects.get_or_create(email=form_data['email'])
    user_ip, uipcreated = UserIP.objects.get_or_create(user=user, ip=ip)
    return user_ip

def store_vehicle(data):
    """
    Deal entry view helper function.
    
    Returns Vehicle.
    """
    vehicle, vcreated = Vehicle.objects.get_or_create(
        make_year=get_make_year(data['obj']['make'], data['text']['year']),
        make=get_make(data['obj']['make']),
        model=get_model(data['obj']['model']))
    return vehicle

def store_dealer(data):
    """
    Deal entry view helper function. Enforces uniqueness by place_id. Assumes
    that Google generates a new place_id if a physical location changes name,
    etc.

    Returns Dealer.
    """
    try:
        dealer = Dealer.objects.get(place_id=data['id'])
    except Dealer.DoesNotExist:
        dealer = Dealer.objects.create(
            place_id=data['id'],
            location=data['location'],
            name=data['name'],
            address=data['vicinity'])
    return dealer

def store_deal(user_ip, vehicle, dealer, data):
    """
    Deal entry view helper function.

    Returns Deal.
    """
    return Deal.objects.create(user_ip=user_ip,
                               vehicle=vehicle,
                               trim=get_trim(data['trim']),
                               dealer=dealer,
                               price=data['price'],
                               date=data['date'],
                               comment=data['comment'])
