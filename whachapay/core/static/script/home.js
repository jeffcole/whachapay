$(function() {

    /**
     * Refresh the select lists when one is selected.
     */
    $('select').change(function() {
        var name = $(this).attr('name');
        var params = getAllSelects();
        params['selected'] = name;

        $.get('/home/update_selections/', params,
              function(data) {
                  if (data) {
                      var value = $('#id_' + name).val();
                      switch (name) {
                      case 'make_year':
                          if (value == 0) {
                              $('#id_make').attr('disabled', true);
                          } else {
                              $('#id_make').attr('disabled', false);
                          }
                          $('#id_model').attr('disabled', true);
                          $('#id_make').html(data.make);
                          $('#id_model').html(data.model);
                          break;
                      case 'make':
                          if (value == 0) {
                              $('#id_model').attr('disabled', true);
                          } else {
                              $('#id_model').attr('disabled', false);
                          }
                          $('#id_model').html(data.model);
                          break;
                      }
                  }
              },
              'json');
    });
    
    /**
     * Get a representation of the state of all select elements.
     * @returns {Object} Keyed according to element name.
     */
    var getAllSelects = function() {
        var selects = {};
        
        $('select').each(function() {
            $.extend(selects, getSelect($(this)));
        });

        return selects;
    }

    /**
     * Get a representation of a select name and value.
     * @param {jQuery object} select The select element object.
     * @returns {Object} Keyed according to element name.
     */
    var getSelect = function(select) {
        var name = select.attr('name');
        var text = select.find(':selected').text();
        // Send the text only when the year has been selected,
        // otherwise send the value.
        var value = (name == 'make_year') ? text : select.val();
        var repr = {};
        repr[name] = value;
        
        return repr;
    }

    /**
     * Initialize the values and enabled states of the select elements.
     */
    var initSelects = function() {
        /** 
         * Reset the year select value. Needed because when using the back
         * button, the make and model selects are no longer populated or
         * selected. Must case out page reload due to field validation, because
         * we still want the fields selected in that case.
         *
         * !!! FIX: Still broken for the case where validation errors shown,
         * corrected, next page loaded, and user clicks back. See:
         * https://developer.mozilla.org/en/DOM/Manipulating_the_browser_history
         */
        if (!($('fieldset>ul.errorlist').length)) {
            $('#id_make_year').val(0);
        }

        var make_year = $('#id_make_year').val();
        var make = $('#id_make').val();
        if (make_year == 0) {
            $('#id_make').attr('disabled', true);
        }
        if (make == 0) {
            $('#id_model').attr('disabled', true);
        }
    }

    /**
     * Set up the location control to use Google autocomplete.
     */
    var initLocation = function() {
        $('#id_location').attr('placeholder', 'Enter a Location');

        var options = {
            //types: ['establishment']
            //types: ['geocode']
        };

        var autocomplete = new google.maps.places.Autocomplete(
            $('#id_location')[0], options);

        google.maps.event.addListener(
            autocomplete, 'place_changed', function() {
                var place = autocomplete.getPlace();
                var placeName, latLng;
                // In case of place not found, 'name' will be the only defined
                // property.
                if (place.geometry) {
                    placeName = place.name;
                    latLng = latLngToString(place.geometry.location);
                } else {
                    placeName = '';
                    latLng = '';
                }
                // Set the hidden fields.
                $('#id_place_name').val(placeName);
                $('#id_lat_lng').val(latLng);
            });
    }

    /**
     * Prevent form submit if location has not been set.
     */
    $('form').submit(function() {
        /**
         * The first condition ensures that the hidden has been set; the second
         * ensures that the hidden value is contained within the text input
         * value (e.g. Honolulu contained within Honolulu, HI). This second
         * condition avoids the case that the user selects a location, clears
         * their selection, then enters a new value without selecting from the
         * autocomplete list.
         */
        if ($('#id_place_name').val() &&
            ($('#id_location').val().indexOf($('#id_place_name').val()) != -1)) {
            return true;
        }
        // !!! FIX: Make consistent with other form errors.
        alert('Please select a location from the list.');
        return false;
    });

    initSelects();
    initLocation();

    /**
     * Location change handler to clear the hiddens and update buttons. This,
     * in combination with updating the buttons in the autocomplete listener,
     * will prevent premature form submit, but produces an ugly button toggle
     * when changing between valid locations.
     */
    // $('#id_location').change(function() {
    //     $('#id_place_name').val('');
    //     $('#id_lat_lng').val('');
    //     updateButtons();
    // });

    /**
     * Enable/disable submit buttons according to hidden location field state.
     */
    // var updateButtons = function() {
    //     if ($('#id_lat_lng').val()) {
    //         $('#enter_btn').attr('disabled', false);
    //         $('#find_btn').attr('disabled', false);
    //     } else {
    //         $('#enter_btn').attr('disabled', true);
    //         $('#find_btn').attr('disabled', true);
    //     }
    // }

});