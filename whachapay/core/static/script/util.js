/**
 * Create a map for a place. Uses the place's location, id, and name.
 * @param {Object} place The place representation object.
 */
var createMap = function(place) {
    var latLng = stringToLatLng(place['location']);
    var options = {
        zoom: 14,
        center: latLng,
        mapTypeId: google.maps.MapTypeId.ROADMAP
    };
    var map = new google.maps.Map($('#' + place['id'])[0], options);
    var marker = new google.maps.Marker({
        position: latLng,
        map: map,
        title: place['name']
    });
}

/**
 * Convert a LatLng to a comma-delimited string.
 * @param {google.maps.LatLng} latLng The object to convert.
 * @returns {String} Format: 'N.N,M.M'
 */
var latLngToString = function(latLng) {
    return latLng.lat() + ',' + latLng.lng();
}

/**
 * Convert a comma-delimited location string to a LatLng.
 * @param {String} Format: 'N.N,M.M'
 * @returns {google.maps.LatLng} latLng The result object.
 */
var stringToLatLng = function(location) {
    var locParts = location.split(',');
    return new google.maps.LatLng(parseFloat(locParts[0]),
                                  parseFloat(locParts[1]));
}
