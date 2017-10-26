Title: QGIS Plugin Development: Using Python Console
Date: 2017-11-02 15:00
Category: QGIS
Tags: python, QGIS
Series: QGIS Plugin Development
Status: draft
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

