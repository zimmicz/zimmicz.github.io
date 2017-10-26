Title: QGIS Plugin Development: Getting Started
Date: 2017-10-26 15:00
Category: QGIS
Tags: python, QGIS
Series: QGIS Plugin Development
Image: https://www.zimmi.cz/posts/assets/qgis-plugin-development-getting-started/qgis.png

QGIS 2.1x is a brilliant tool for Python-based automation in form of custom scripts or even plugins. The first steps towards writing the custom code might be a bit difficult, as you need to grasp quite complex Python API. The *QGIS Plugin Development* series (see the list of other parts at the end of this article) targets pitfalls and traps I've met while learning to use it myself.

The outcome of the series is going to be **a fully functional custom plugin** capable of writing attribute values from a source layer nearest neighbour to a target layer based on their spatial proximity.

In this part, I'll mention the basics a.k.a. what is good to know before you start.

## Documentation

Different QGIS versions come with different Python API. The documentation is to be found at [https://qgis.org](http://qgis.org), the latest being [version 2.18](http://qgis.org/api/2.18/). Note that if you come directly to [http://qgis.org/api/](http://qgis.org/api/), you'll see the current master docs.

Alternatively, you can `apt install qgis-api-doc` on your Ubuntu-based system and run `python -m SimpleHTTPServer [port]` inside `/usr/share/qgis/doc/api`. You'll find the documentation at [http://localhost:8000](http://localhost:8000) (if you don't provide port number) and it will be available even when you're offline.

## Basic API objects structure

Before launching QGIS, take a look at what's available inside API:

* **qgis.core** package brings all the basic objects like QgsMapLayer, QgsDataSourceURI, QgsFeature etc
* **qgis.gui** package brings GUI elements that can be used within QGIS like QgsMessageBar or QgsInterface (very important API element, exposed to all custom plugins)
* **qgis.analysis**, **qgis.networkanalysis**, **qgis.server**, and **qgis.testing** packages that won't be covered in the series
* **qgis.utils** module that comes with `iface` exposed (very handy within QGIS Python console)

## QGIS Python Console

Using Python console is the easiest way to automate your QGIS workflow. It can be accessed via pressing `Ctrl + Alt + P` or navigating to `Plugins -> Python Console`. Note the above mentioned `iface` from **qgis.utils** module is exposed by default within the console, letting you interact with QGIS GUI. Try out the following examples.

    :::python
    iface.mapCanvas().scale() # returns the current map scale
    iface.mapCanvas().zoomScale(100) # zoom to scale of 1:100
    iface.activeLayer().name() # get the active layer name
    iface.activeLayer().startEditing() # toggle editting

That was a very brief introduction to QGIS API, the next part will walk you through the console more thoroughly.
