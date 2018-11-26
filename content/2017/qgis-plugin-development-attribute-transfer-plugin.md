Title: QGIS Plugin Development: AttributeTransfer Plugin
Date: 2017-11-23 19:00
Category: QGIS
Tags: python, QGIS
Series: QGIS Plugin Development
Image: https://www.zimmi.cz/posts/assets/qgis-plugin-development-attribute-transfer-plugin/qgis.png

This part finally brings [the whole source code of the QGIS AttributeTransfer plugin](https://github.com/zimmicz/qgis-attribute-transfer-plugin).

<div class="text-center"><img src="/posts/assets/qgis-plugin-development-attribute-transfer-plugin/qgis.gif"/></div>

The plugin itself resides in the [`attribute_transfer.py`](https://github.com/zimmicz/qgis-attribute-transfer-plugin/blob/master/attribute_transfer.py) file. When `run()` method is invoked, the QT form pops up with combos prefilled with available vector layers that support attribute editing.

Source and target layer combos are mutually exclusive, thus it's not possible to transfer the attribute within the same layer.

Coding the plugin, I came across minor issues related mainly to the `QgsSpatialIndex` implementation. In [the nearest neighbor analysis part]({filename}../2017/qgis-plugin-development-finding-nearest-neighbors.md) of the series, the `QgsSpatialIndex.nearestNeighbor` method was mentioned. Yet, as I found out, this method only works with `QgsPoint` geometries. Those are impossible to get from `QgsPolygon` or `QgsPolyline`, though. What can one possibly do, facing such a misfortune? Well&hellip; draw a solution matrix.

|         | point                           | line                                                                                 | polygon                                                                                 |
|---------|---------------------------------|--------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------|
| **point**   | QgsSpatialIndex.nearestNeighbor | QgsSpatialIndex.nearestNeighbor; layers have to be switched, e.g. source layer = line | QgsSpatialIndex.nearestNeighbor; layers have to be switched, e.g. source layer = polygon |
| **line**    | QgsSpatialIndex.nearestNeighbor | QgsSpatialIndex.intersects with QgsGeometry.distance                                  | QgsSpatialIndex.intersects with QgsGeometry.distance                                     |
| **polygon** | QgsSpatialIndex.nearestNeighbor | QgsSpatialIndex.intersects with QgsGeometry.distance                                  | QgsSpatialIndex.intersects with QgsGeometry.distance                                     |

Using the spatial index brings one more issue I've come to realize just after implementing the special comparison workflows for different geometry types. There's a chance of finding the nearest feature using the bounding box that's actually *not* the nearest feature. In that case, I chose to find the most distant vertex of such a feature and use it to construct the rectangle around the target feature. If there are any source features in such a rectangle, it's very likely one of them is the *real* nearest feature.

<div class="text-center"><img src="/posts/assets/qgis-plugin-development-attribute-transfer-plugin/qgis.png"/></div>
Right now, I'm working on [finding the nearest feature even if no bounding box intersection is found](https://github.com/zimmicz/qgis-attribute-transfer-plugin/issues/3). Meanwhile, [the plugin is being reviewed](https://github.com/zimmicz/qgis-attribute-transfer-plugin/issues/2) to be featured in [QGIS Plugins repository](https://plugins.qgis.org). Fingers crossed.

I thought this was going to be the last part of the series. But how could one possibly claim the coding project done without writing *tests*? Stay tuned for the next episode.
