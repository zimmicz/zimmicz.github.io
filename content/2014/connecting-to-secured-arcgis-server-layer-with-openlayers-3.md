Title: Connecting To Secured ArcGIS Server Layer With OpenLayers 3
Date:  2014-09-12 18:03
Category: web maps
Tags: javascript, openlayers, ogc

I was made to use ArcGIS Server with [Openlayers 3](http://openlayers.org) just recently as one of the projects I've been working on demands such different tools to work together.

**tl;dr: I hate Esri.**

I found myself in need to access secured layers published via WMS on ArcGIS Server using username and password I was given, so here's a little how-to for anyone who would have to do the same.

Let's start with a simple ol.layer.Image and pretend this is the secured layer we're looking for:

    var layer = new ol.layer.Image({
        extent: extent,
        source: new ol.source.ImageWMS(/** @type {olx.source.ImageWMSOptions} */ ({
            url: url,
            params: {
                'LAYERS': 'layer',
                'CRS': 'EPSG:3857',
            }
        }))
    });

We need to retrieve the token, so we define a function:

    function retrieveToken(callback) {
        var req = new XMLHttpRequest;

        req.onload = function() {
            if (req.status == "200") {
                var response = JSON.parse(req.responseText);
                if (response.contents) {
                    callback(response.contents); // response contents is where the token is stored
            }
        };
        req.open("get", "http://server.address/arcgis/tokens/?request=getToken&username=username&password=password&expiration=60", true);
        req.send()
    }

I pass a parameter called `callback` - that's a very important step, otherwise you would not be able to retrieve the token when you actually need it (AJAX stands for asynchronous). Now you just pass the token to the layer params like this:

    retrieveToken(function(token) {
        layer.getSource().updateParams({
            token: token
        })
    }

When you open Firebug and inspect Network tab, you should find `token` URL parameter passed along with WMS `GetMap` request.

Few sidenotes:

1. Although you might be logged in ArcGIS Server via web interface, you might need to pass the `token`  URL param when trying to access Capabilities document. Don't know why though.
2. You should probably take care of calling the `retrieveToken()` in shorter interval than the token expiration is set to. Otherwise you might end up with invalid token.
3. You need to hide the username and password from anonymous users (I guess that's only possible with server side implementation of selective JavaScript loading).
