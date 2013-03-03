from django.db import models
from core import util

class Make(models.Model):
    """Populated via fixture."""
    name = models.CharField(max_length=100)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['name']

class MakeYear(models.Model):
    """Populated via fixture."""
    make = models.ForeignKey(Make)
    year = models.IntegerField()

    def __unicode__(self):
        return util.get_unicode(self.make, self.year)

    class Meta:
        ordering = ['make', '-year']

class Model(models.Model):
    """Populated via fixture."""
    make = models.ForeignKey(Make)
    name = models.CharField(max_length=100)

    def __unicode__(self):
        return util.get_unicode(self.make, self.name)

    class Meta:
        ordering = ['make', 'name']

class ModelYear(models.Model):
    """Populated via fixture."""
    model = models.ForeignKey(Model)
    year = models.IntegerField()

    def __unicode__(self):
        return util.get_unicode(self.model, self.year)

    class Meta:
        ordering = ['model', '-year']

class Trim(models.Model):
    """Populated via fixture."""
    model = models.ForeignKey(Model)
    name = models.CharField(max_length=100)

    def __unicode__(self):
        return util.get_unicode(self.model, self.name)

    class Meta:
        ordering = ['model', 'name']

class TrimYear(models.Model):
    """Populated via fixture."""
    trim = models.ForeignKey(Trim)
    year = models.IntegerField()

    def __unicode__(self):
        return util.get_unicode(self.trim, self.year)

    class Meta:
        ordering = ['trim', '-year']

class Vehicle(models.Model):
    """
    Populated at time of deal creation in order to reduce fixture maintenance.
    """
    make_year = models.ForeignKey(MakeYear)
    make = models.ForeignKey(Make)
    model = models.ForeignKey(Model)

    def __unicode__(self):
        return util.get_unicode(self.make_year.year, self.make.name, self.model.name)

    class Meta:
        ordering = ['make_year', 'make', 'model']

class User(models.Model):
    email = models.EmailField(max_length=100)

    def __unicode__(self):
        return self.email

    class Meta:
        ordering = ['email']

class IPAddress(models.Model):
    ip = models.IPAddressField(unique=True)

    def __unicode__(self):
        return self.ip

    class Meta:
        ordering = ['ip']
        verbose_name = 'IP address'
        verbose_name_plural = 'IP addresses'

class UserIP(models.Model):
    """
    Mapping table between Users and IPs. djangoappengine does not support
    ManyToManyField.
    """
    user = models.ForeignKey(User)
    ip = models.ForeignKey(IPAddress)

    def __unicode__(self):
        return util.get_unicode(self.user, self.ip)

    class Meta:
        ordering = ['user', 'ip']
        verbose_name = 'user IP'
        verbose_name_plural = 'user IPs'

class Dealer(models.Model):
    place_id = models.CharField(max_length=40, unique=True)
    location = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    # !!! FIX: Store address parts to make formatting easier. Will have to make
    # a place detail request.
    address = models.CharField(max_length=200)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['name']

class Deal(models.Model):
    user_ip = models.ForeignKey(UserIP)
    vehicle = models.ForeignKey(Vehicle)
    trim = models.ForeignKey(Trim)
    dealer = models.ForeignKey(Dealer)
    price = models.IntegerField()
    date = models.DateField()
    comment = models.TextField(blank=True)

    def __unicode__(self):
        return util.get_unicode(self.user_ip, self.vehicle, self.dealer,
                                self.price, self.date)

    class Meta:
        ordering = ['vehicle', 'dealer', 'price']
