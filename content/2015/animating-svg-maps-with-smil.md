Title: Animating SVG Maps With SMIL
Date: 2015-04-29 18:24
Tags: svg, smil
Category: web maps

Using SVG to build web maps have both pros and cons and to be honest I don't know any *serious* map/GIS project built on top of SVG. However, as a part of my job at university, I was forced to use both SVG and SMIL to produce animated web map (see the small version below or the big one at [GitHub](https://zimmicz.github.io/svg-smil-airplanes/map.svg)) and I'd like to share my findings.

<object width="400" data="https://zimmicz.github.io/svg-smil-airplanes/map.svg" type="image/svg+xml"></object>

## Data preprocessing
I chose [Natural Earth dataset](http://www.naturalearthdata.com/) both for basemap and thematic layer:

- countries polygon layer for basemap
- airports point layer for thematic layer

I decided that animation should go like this:

1. Load basemap and Vaclav Havel airport (PRG).
2. Animate destinations one by one. They are revealed in order of their distance from PRG.
3. Animate airways.
4. Once airways are animated, animate airplanes along their path from PRG to their destination in order of their time of departure.
5. Profit.

My goal was to create an animation of all departures from Vaclav Havel airport during one day. These data can be obtained at [FlightStats](http://www.flightstats.com/), I didn't find a way make this process automatic though. [OpenFlights](http://openflights.org/) might be better source then.

## SVG creation
[Kartograph](http://kartograph.org/) is a great tool both for SVG generation and scripting. What a pity it's probably a dead project according to the last commit date. After installing Python part of library used to create SVG files out of vector geometries, it can be run with something like this:

    kartograph --output map.svg --pretty-print --style style.css config.json

Pretty self-explanatory, let's have a look at config file:

    :::javascript
    {
        "layers": {
            "countries": {
                "src": "ne_50m_admin_0_countries/ne_50m_admin_0_countries.shp",
                "attributes": ["name"]
            },
            "airports": {
                "src": "ne_10m_airports/ne_10m_airports_prg.shp",
                "attributes": ["name", "abbrev"]
            },
            "travels": {
                "src": "ne_10m_airports/travels.shp",
                "attributes": ["time", "distance"]
            },
            "grid": {
                "special": "graticule",
                "latitudes": 10,
                "longitudes": 10
            }
        },
        "proj": {
            "id": "satellite",
            "lon0": 0.0,
            "lat0": 48.0,
            "dist": 45,
            "up": 15
        },
        "bounds": {
            "mode": "bbox",
            "data": [-180, -90, 180, 90],
            "padding": 1
        },
        "export": {
            "round": 1,
            "width": 1000,
            "ratio": 1
        }
    }

It is possible to adjust map settings in many different ways. The most important/interesting:

- Choose what attributes you want to have exported from source file with `attributes` key for every layer. They'll be available as `data-` attribute of SVG elements.
- It comes with Grid generation packed in! Really great. Sea generation works for some projections only.
- Set the projections you want to use with additional settings.
- `bounds` settings should - according to the docs - use layer extent as well, I couldn't make it work though. Use `[-180, -90, 180, 90]` as a workaround to get the whole world. Don't forget to set `padding`, so your map doesn't get clipped on edges.
- `export`ing coordinates rounded to one decimal place makes your SVG a lot smaller.

You can change SVG look with simple CSS, just be sure to use layer names as CSS ids:

    #airports {
        fill: #CC0000;
        fill-opacity: 0;
        stroke: #660000;
        stroke-opacity: 0;
    }

    #countries {
        fill: #e6deb4;
        stroke: #a59f81;
    }

    #grid {
        stroke: #d0d0d0;
        stroke-width: .3px;
    }

    #travels {
        stroke: #1f78b4;
        stroke-opacity: 0;
        stroke-dasharray: 5,5;
    }

## Data adjustment & animation

**SMIL** is a XML based language for multimedia representation. It comes ready for timing, animation, visual transitions etc. I guess it might be considered easier to read for a web development beginner. Once you start using it, you immediately realize it suffers from the same disease like XML does: it is so wordy!

Let's get back to my example. To animate airports one by one, let's give them unique ids, so they look something like:

    :::xml
    <circle id="brs" stroke-opacity="0" fill-opacity="0" cx="476.597304864" cy="539.487783171" data-abbrev="BRS" data-name="Bristol Int'l" r="3"/>

That's something you do by hand as kartograph doesn't give ids to SVG elements. Once you're done with that, you can run SMIL animation. If you look closer at the final map, you'll notice there are three properties animated for each airport: fill opacity, stroke opacity and radius. Each property needs to use separate SMIL `<animate />`, which might look like the one below:

    :::xml
    <animate attributeName="fill-opacity"
        id="kos_ani_fo"
        from="0"
        to="1"
        begin="osr_ani.end"
        dur="0.25s"
        fill="freeze"
        xlink:href="#kos"
    />
    <animate attributeName="stroke-opacity"
        id="kos_ani_so"
        from="0"
        to="1"
        begin="osr_ani.end"
        dur="0.25s"
        fill="freeze"
        xlink:href="#kos"
    />
    <animate attributeName="r"
        id="kos_ani_r"
        from="10px"
        to="3px"
        begin="osr_ani.end"
        dur="0.25s"
        xlink:href="#kos"
    />

I guess you get the idea how long this would take for more airports. Make sure to notice that SMIL can start animation based on another animation's end (`osr_ani.end`) - that's pretty neat.

Airways animation works almost the same. First, add unique id to each airway:

    :::xml
    <path d="M550.9,562.9L568.0,495.0 " id="travel-arn"/>

Second, start animation after all the airports are visible on the map. Notice the initial definition of `d` attribute - it's a line with zero length.

    :::xml
    <animate attributeName="d"
        id="path_ani"
        from="M550.9,562.9L550.9,562.9"
        to="M550.9,562.9L568.0,495.0"
        begin="icn_ani_r.end"
        dur="3s"
        xlink:href="#travel-arn"
    />

Once airways animation has finished, let airplanes fly around the globe with a simple JavaScript function:

    /**
     * @param  number coef  scale radius by number of flights to the given destination
     * @param  string flight_id
     */
    var circle = function(coef, flight_id, timeshift) {
        var svgns = "http://www.w3.org/2000/svg";
        var svgDocument =document;
        var motion = svgDocument.createElementNS(svgns,"animateMotion");
        var animation = svgDocument.createElementNS(svgns,"animate");
        var shape  = svgDocument.createElementNS(svgns, "circle");
        var time = 15 + timeshift;
        var dur = document.getElementById(flight_id).getAttributeNS(null, "data-dist")/100;
        motion.setAttribute("begin", time + "s");
        motion.setAttribute("dur", dur + "s");
        motion.setAttribute("path", document.getElementById(flight_id).getAttributeNS(null, "d"));
        motion.setAttribute("xlink:href", "#" + flight_id);
        motion.setAttribute("id", flight_id + "_motion");

        animation.setAttribute("attributeName", "opacity");
        animation.setAttribute("from", "1");
        animation.setAttribute("to", "0");
        animation.setAttribute("begin", time + dur + "s");
        animation.setAttribute("dur", "0.1s");
        animation.setAttribute("fill", "freeze");


        shape.setAttributeNS(null, "r",  1*coef);
        shape.setAttributeNS(null, "fill", "1f78b4");
        shape.setAttributeNS(null, "stroke", "1f78b4");
        shape.setAttribute("id", "airplane-" + flight_id);
        shape.appendChild(motion);
        shape.appendChild(animation);

        document.getElementById("airplanes").appendChild(shape);
    }

SMIL with SVG seems to be interesting option for web map animation, a bit lengthy though. Syncing animations can easily become pain in the ass ([see StackOverflow thread](https://stackoverflow.com/questions/29897355/svg-smil-animatemotion-only-triggers-once/)). Never call your function `animate` - there is namesake function defined in [Web Animations API](https://w3c.github.io/web-animations/) that makes animation crash in Chrome. `<animateMotion />` is a great tool to animate elements along path.
