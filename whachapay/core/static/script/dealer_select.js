$(function() {

    // The places variable is set via script tag in the page template.
    var l = places.length;
    for (var i = 0; i < l; i++) {
        createMap(places[i]);
    }

});