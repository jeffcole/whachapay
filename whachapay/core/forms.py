import pprint
from django import forms
from django.core.exceptions import ValidationError
from core.models import MakeYear
from core.queries import get_trim_options

_pp = pprint.PrettyPrinter(indent=2)

def validate_make_year(value):
    validate_positive(value, 'Year')

def validate_trim(value):
    validate_positive(value, 'Trim')

def validate_positive(value, name):
    """Validate that a value is an integer greater than zero."""
    args = {'value': value, 'name': name}
    try:
        v = int(value)
        if v <= 0:
            raise ValidationError(u'%(name)s is required.' % args)
    except ValueError:
        raise ValidationError(u'Select a valid %(name)s. %(value)s is not one of the available choices.'
                              % args)

class AjaxChoiceField(forms.ChoiceField):
    """
    ChoiceField subclass to allow for a selected value that is not in the
    field's choices, because the choices are loaded via ajax.
    """
    def validate(self, value):
        """
        Skips ChoiceField validation, which would normally validate that the
        input is in self.choices.
        """
        super(forms.ChoiceField, self).validate(value)
        validate_positive(value, self.label)

class HomeForm(forms.Form):
    # Get distinct make_years.
    make_year_choices = [(year, year) for year in MakeYear.objects.values_list(
            'year', flat=True).distinct().order_by('year')]
    make_year_choices.insert(0, (0, 'Year'))
    make_year = forms.ChoiceField(label='Year', choices=make_year_choices,
                                  validators=[validate_make_year])

    """
    1) The choices for these fields are loaded via Ajax.
    2) label is specified because the auto label is not present at the time of
       AjaxChoiceField.validate().
    3) error_messages is specified because the required error will be triggered
       by the superclass validate(), rather than validate_positive().
    """
    make = AjaxChoiceField(choices=[(0, 'Make')], label='Make',
                           error_messages={'required': 'Make is required.'})
    model = AjaxChoiceField(choices=[(0, 'Model')], label='Model',
                           error_messages={'required': 'Model is required.'})

    # Google places Autocomplete
    location = forms.CharField(min_length=1, max_length=200,
                               error_messages={'required': 'Location is required.'})
    # These fields are set via JavaScript with values from the Autocomplete
    # class.
    place_name = forms.CharField(widget=forms.HiddenInput)
    lat_lng = forms.CharField(widget=forms.HiddenInput)

class TrimForm(forms.Form):
    trim = forms.ChoiceField()

    def __init__(self, *args, **kwargs):
        """Load the available trims for the given model and year."""
        # Need to pop these before calling super().__init__.
        model_pk = kwargs.pop('model_pk')
        trim_year = kwargs.pop('trim_year')
        super(TrimForm, self).__init__(*args, **kwargs)
        self.fields['trim'].choices = (
            [(m.id, m.name) for m in get_trim_options(model_pk, trim_year)])
        self.fields['trim'].choices.insert(0, (0, 'All Trims'))
        self.fields['trim'].initial = 0

class EntryForm(TrimForm):
    price = forms.IntegerField(min_value=100, max_value=1000000)
    date = forms.DateField()
    comment = forms.CharField(widget=forms.Textarea, max_length=2000,
                              required=False)
    email = forms.EmailField(max_length=100)

    def __init__(self, *args, **kwargs):
        """Update the extra choice in the trim field, and set its validators."""
        super(EntryForm, self).__init__(*args, **kwargs)
        del self.fields['trim'].choices[0]
        self.fields['trim'].choices.insert(0, (0, 'Select'))
        self.fields['trim'].initial = 0
        self.fields['trim'].validators = [validate_trim]
