Title: QGIS Plugin Development: Using Python Console
Date: 2017-11-02 15:00
Category: QGIS
Tags: python, QGIS
Series: QGIS Plugin Development
Image: https://www.zimmi.cz/posts/assets/qgis-plugin-development-using-python-console/qgis.png

As mentioned in [previous part]({filename}../2017/qgis-plugin-development-getting-started.md) of the series, the QGIS Python console is an entry point to GIS workflow automation within QGIS. Remember there's an `iface` object representing `qgis.gui.QgisInterface` instance within the console that gives you access to the whole QGIS GUI. Let's see what we can do inside the console.

## Loading vector layers folder

    :::python
    import glob
    from qgis.core import QgsMapLayerRegistry, QgsVectorLayer

    def load_folder(folder):
        VALID_EXTENSIONS = ('.geojson', '.gpkg', '.shp')
        files = [f for f in glob.glob("{}/*".format(folder)) if f.endswith(VALID_EXTENSIONS)]

        for f in files:
            layer = QgsVectorLayer(f, f.split('/')[-1], 'ogr')

            if not layer.isValid():
                iface.messageBar().pushCritical("Failed to load:", f)
                continue

            QgsMapLayerRegistry.instance().addMapLayer(layer)

    load_folder("path/to/your/vector/files/folder")

* `QgsMapLayerRegistry` represents *Layers Panel* as present in the QGIS GUI
* `iface.messageBar()` returns the message bar of the main app and lets you notify the user of what's going on under the hood
* `QgsVectorLayer` represents a vector layer with its underlying vector data sets

## Editing active layer attribute table

The following code demonstrates the possibility to edit vector layer attribute table via console.

* Any attribute to be written has to come in form of a `qgis.core.QgsField` - this is more or less an encapsulation of an attribute name and its type (`PyQt4.QtCore.QVariant` to be precise)
* The underlying data provider has to be capable of attribute addition (`caps & QgsVectorDataProvider.AddAttributes`)
* `QgsVectorLayer.addAttribute` method returns boolean rather than throwing an exception

<!-- -->
    :::python
    from qgis.core import QgsField
    from qgis.gui import QgsMessageBar
    from PyQt4.QtCore import QVariant


    def edit_active_layer(attr_name, attr_type):
        layer = iface.activeLayer()
        caps = layer.dataProvider().capabilities()

        if caps & QgsVectorDataProvider.AddAttributes:
            layer.startEditing()
            if layer.addAttribute(QgsField(attr_name, attr_type)):
                iface.messageBar().pushMessage("Attribute {0} was successfully added to the active layer.".format(attr_name), QgsMessageBar.SUCCESS)
                layer.commitChanges()
            else:
                iface.messageBar().pushMessage("Attribute {0} was not added. Does it already exist?".format(attr_name), QgsMessageBar.CRITICAL)
                layer.rollBack()

    edit_active_layer("new_string_attribute", QVariant.String)

The whole series aims to present a plugin capable of writing a new attribute and its value to an existing layer. Thus, this code might come handy in the future.

## Creating a new vector layer

It's possible to create a whole new vector layer with QGIS Python console. I present a very simple `create_new_layer` function, yet I hope you can imagine the ways it can be tweaked.

    :::python
    from qgis.core import QgsField, QgsFields, QgsVectorLayer, QgsFeature, QgsGeometry, QgsPoint
    from PyQt4.QtCore import QVariant

    def create_new_layer():
        filename = "/path/to/your/vector/file.gpkg"

        fields = QgsFields()
        fields.append(QgsField("attr1", QVariant.String))
        fields.append(QgsField("attr2", QVariant.Int))

        file = QgsVectorFileWriter(
            filename,
            "UTF8",
            fields,
            QGis.WKBPoint,
            QgsCoordinateReferenceSystem(4326),
            "GPKG"
        )

        layer = QgsVectorLayer(filename, filename.split("/")[-1], "ogr")
        QgsMapLayerRegistry.instance().addMapLayer(layer)

        if not layer.dataProvider().capabilities() & QgsVectorDataProvider.AddAttributes:
            pass

        feature = QgsFeature(layer.pendingFields())
        feature.setGeometry(QgsGeometry().fromPoint(QgsPoint(0, 0)))
        feature.setAttribute("attr1", "attr1")
        feature.setAttribute("attr2", 2)

        layer.startEditing()

        if layer.addFeature(feature, True):
            layer.commitChanges()
        else:
            layer.rollBack()
            iface.messageBar().pushMessage("Feature addition failed.", QgsMessageBar.CRITICAL)

    create_new_layer()

Those were just few examples of what can be done with QGIS API and Python console. Next time, I'd like to focus on spatial joins inside QGIS - another step to the final plugin.
