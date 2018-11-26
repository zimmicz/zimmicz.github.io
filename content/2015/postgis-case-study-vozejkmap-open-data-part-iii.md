Title: PostGIS Case Study: Vozejkmap Open Data (Part III)
Date: 2015-11-14 20:39
Tags: postgresql, postgis, leaflet, javascript
Category: web maps

After a while I got back to my [PostGIS open data]({filename}../2014/postgis-case-study-vozejkmap-open-data-part-i.md) [case study]({filename}postgis-case-study-vozejkmap-open-data-part-ii.md). Last time I left it with clustering implemented, looking forward to incorporate [Turf.js](http://turfjs.org) in the future. *And the future is now.* [The code is still available on GitHub.](https://github.com/zimmicz/vozejkmap-to-postgis)

## Subgroup clustering
Vozejkmap data is categorized based on the place type (banks, parking lots, pubs, &hellip;). One of the core features of map showing such data should be the easy way to turn these categories on and off.

As far as I know, it's not trivial to do this with the standard Leaflet library. Extending `L.control.layers` and implement its `addOverlay`, `removeOverlay` methods on your own might be the way to add needed behavior. Fortunately, there's an easier option thanks to [Leaflet.FeatureGroup.SubGroup](https://github.com/ghybs/Leaflet.FeatureGroup.SubGroup) that can handle such use case and is really straightforward. See the code below.

    :::javascript
    cluster = L.markerClusterGroup({
        chunkedLoading: true,
        chunkInterval: 500
    });

    cluster.addTo(map);

    ...

    for (var category in categories) {
        // just use L.featureGroup.subGroup instead of L.layerGroup or L.featureGroup
        overlays[my.Style.set(category).type] = L.featureGroup.subGroup(cluster, categories[category]);
    }

    mapkey = L.control.layers(null, overlays).addTo(map);

With this piece of code you get a map key with checkboxes for all the categories, yet they're still kept in the single cluster on the map. Brilliant!

<img src="/posts/assets/postgis-case-study-vozejkmap-open-data-part-iii/map.png" title="vozejkmap.cz data map" class="img-responsive centered">

## Using Turf.js for analysis

Turf is one of those libraries I get amazed easily with, spending a week trying to find a use case, finally putting it aside with *"I'll get back to it later"*. I usually don't. This time it's different.

I use Turf to get the nearest neighbor for any marker on click. My first try ended up with the same marker being the result as it was a member of a feature collection passed to `turf.nearest()` method. After snooping around the docs I found `turf.remove()` method that can filter GeoJSON based on key-value pair.

Another handy function is `turf.distance()` that gives you distance between two points. The code below adds an information about the nearest point and its distance into the popup.

    :::javascript
    // data is a geojson feature collection
    json = L.geoJson(data, {
        onEachFeature: function(feature, layer) {
            layer.on("click", function(e) {
                var nearest = turf.nearest(layer.toGeoJSON(), turf.remove(data, "title", feature.properties.title)),
                    distance = turf.distance(layer.toGeoJSON(), nearest, "kilometers").toPrecision(2),
                    popup = L.popup({offset: [0, -35]}).setLatLng(e.latlng),
                    content = L.Util.template(
                        "<h1>{title}</h1><p>{description}</p> \
                        <p>Nejbližší bod: {nearest} je {distance} km daleko.</p>", {
                        title: feature.properties.title,
                        description: feature.properties.description,
                        nearest: nearest.properties.title,
                        distance: distance
                    });

                popup.setContent(content);
                popup.openOn(map);

                ...

From what I've tried so far, Turf seems to be incredibly fast and easy to use. I'll try to find the nearest point for any of the categories, that could take Turf some time.

## Update

Turf is blazing fast! I've implemented nearest point for each of the categories and it gets done in a blink of an eye. Some screenshots below. Geolocation implemented as well.

<p><img src="/posts/assets/postgis-case-study-vozejkmap-open-data-part-iii/screen1.png" title="vozejkmap.cz data map" class="img-responsive centered"> You can locate the point easily.</p>
<p><img src="/posts/assets/postgis-case-study-vozejkmap-open-data-part-iii/screen2.png" title="vozejkmap.cz data map" class="img-responsive centered"> You can hide the infobox.</p>
<p><img src="/posts/assets/postgis-case-study-vozejkmap-open-data-part-iii/screen3.png" title="vozejkmap.cz data map" class="img-responsive centered">You can jump to any of the nearest places.</p>
