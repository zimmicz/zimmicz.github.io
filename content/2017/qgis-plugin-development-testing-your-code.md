Title: QGIS Plugin Development: Testing Your Code
Date: 2017-11-30 17:36
Category: QGIS
Tags: python, QGIS
Series: QGIS Plugin Development

Good news, everyone! The [AttributeTransfer](https://plugins.qgis.org/plugins/AttributeTransfer/) plugin has been approved for [QGIS Python Plugins Repository](https://plugins.qgis.org/plugins/). It's available via QGIS *Manage and Install Plugins* menu. Feel free to download!

Nevertheless, this post (the last in the series) covers QGIS plugin testing rather than my personal feelings about the aforementioned success.

## Testing means mocking

To test a QGIS plugin you need to simulate the environment it's meant to run in. And that environment is obviously QGIS itself, yet it's not feasible to launch QGIS every time you run a test. Luckily, [there's a great `QGIS` mock](https://github.com/zimmicz/qgis-attribute-transfer-plugin/blob/master/tests/utilities.py) that gets you going in no time (it completely slipped my mind where I found that piece of code though).

## Testing means you need data

Every test is run again and again, which means it has to reset the data being used to its default state. This might be a PIDA if the test changes the data in an unpredictable manner.

Using QGIS memory layers [you can prepare fresh data](https://github.com/zimmicz/qgis-attribute-transfer-plugin/blob/master/tests/create_dummy_data.py) for each of your tests, effectively putting the whole data manipulation process aside.

## Writing tests

Each of the AttributeTransfer plugin tests inherits from `unittest.TestCase`, which comes with several methods you might be familiar with from other languages: `setUp()` is run before for every test method, while `tearDown()` is run after each of them. Tests are defined as methods whose names start with the word `test`.

Each test should call some `assertWhatever` method that checks whether the test passed or failed. Here's an example of such a test covering non-point layers.

    :::python
    #!/usr/bin/env python
    # -*- coding: utf-8 -*-
    # @Date    : 2017-11-18 18:40:50
    # @Author  : Michal Zimmermann <zimmicz@gmail.com>

    import os
    import sip
    import sys
    import unittest
    from qgis.core import QgsMapLayerRegistry, QgsVectorLayer, QgsFeature, QgsGeometry, QgsPoint
    from utilities import get_qgis_app

    sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
    from attribute_transfer import AttributeTransfer
    from create_dummy_data import create_dummy_data_polygon_or_line

    sip.setapi('QtCore', 2)
    sip.setapi('QString', 2)
    sip.setapi('QDate', 2)
    sip.setapi('QDateTime', 2)
    sip.setapi('QTextStream', 2)
    sip.setapi('QTime', 2)
    sip.setapi('QUrl', 2)
    sip.setapi('QVariant', 2)

    QGIS_APP = get_qgis_app()
    IFACE = QGIS_APP[2]


    class AttributeTransferTestPolygonOrLine(unittest.TestCase):

        def setUp(self):
            self.source_layer = QgsVectorLayer(
                "Polygon?crs=epsg:4326&field=id:integer&field=textAttr:string&field=intAttr:integer&field=decAttr:double&field=dateAttr:date&index=yes", "source layer", "memory")
            self.target_layer = QgsVectorLayer(
                "Linestring?crs=epsg:4326&field=id:integer&index=yes", "target layer", "memory")
            self.widget = AttributeTransfer(IFACE)

            registry = QgsMapLayerRegistry.instance()
            registry.removeAllMapLayers()
            registry.addMapLayers([self.source_layer, self.target_layer])
            create_dummy_data_polygon_or_line(self.source_layer, self.target_layer)
            self.widget.initGui()
            self.widget.vectors = [self.source_layer, self.target_layer]
            self.widget.editable_vectors = [self.source_layer, self.target_layer]
            self.widget.dlg.sourceLayer.addItems(["source layer", "target layer"])

        def test_text_attr(self):
            ATTRIBUTE_NAME = "textAttr"
            ATTRIBUTE_INDEX = 1

            self._test_attr(ATTRIBUTE_NAME, ATTRIBUTE_INDEX)

        def test_int_attr(self):
            ATTRIBUTE_NAME = "intAttr"
            ATTRIBUTE_INDEX = 2

            self._test_attr(ATTRIBUTE_NAME, ATTRIBUTE_INDEX)

        def test_dec_attr(self):
            ATTRIBUTE_NAME = "decAttr"
            ATTRIBUTE_INDEX = 3

            self._test_attr(ATTRIBUTE_NAME, ATTRIBUTE_INDEX)

        def test_date_attr(self):
            ATTRIBUTE_NAME = "dateAttr"
            ATTRIBUTE_INDEX = 4

            self._test_attr(ATTRIBUTE_NAME, ATTRIBUTE_INDEX)

        def test_existing_attr(self):
            ATTRIBUTE_NAME = "id"
            ATTRIBUTE_INDEX = 0

            self.widget.dlg.sourceAttribute.setCurrentIndex(ATTRIBUTE_INDEX)
            self.widget.dlg.targetAttribute.setText(ATTRIBUTE_NAME)

            self.assertEqual(
                self.widget.dlg.sourceAttribute.currentText(), ATTRIBUTE_NAME)
            self.assertFalse(self.widget.transfer())

        def _test_attr(self, attr_name, attr_index):
            self.widget.dlg.sourceAttribute.setCurrentIndex(attr_index)
            self.widget.dlg.targetAttribute.setText(attr_name)

            self.assertEqual(
                self.widget.dlg.sourceAttribute.currentText(), attr_name)

            self.widget.transfer()

            target_fields = [f.name()
                             for f in self.target_layer.dataProvider().fields()]
            self.assertIn(attr_name, target_fields)

            source_features = [f for f in self.source_layer.getFeatures()]
            target_features = [f for f in self.target_layer.getFeatures()]

            for idx, f in enumerate(source_features):
                self.assertEqual(f.attribute(attr_name), target_features[
                                 idx].attribute(attr_name))


    if __name__ == "__main__":
        unittest.main()