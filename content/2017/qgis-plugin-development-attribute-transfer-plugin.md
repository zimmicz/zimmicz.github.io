Title: QGIS Plugin Development: AttributeTransfer Plugin
Date: 2017-11-23 19:00
Category: QGIS
Tags: python, QGIS
Series: QGIS Plugin Development
Image: https://www.zimmi.cz/posts/assets/qgis-plugin-development-attribute-transfer-plugin/qgis.png

This part finally brings [the whole source code of the QGIS AttributeTransfer plugin](https://github.com/zimmicz/qgis-attribute-transfer-plugin).

<div class="text-center"><img data-echo="/posts/assets/qgis-plugin-development-attribute-transfer-plugin/qgis.gif"/></div>

The plugin itself resides in the [`attribute_transfer.py`](https://github.com/zimmicz/qgis-attribute-transfer-plugin/blob/master/attribute_transfer.py) file. When `run()` method is invoked, the QT form pops up with combos prefilled with available vector layers that support attribute editing.

Source and target layer combos are mutually exclusive, thus it's not possible to transfer the attribute within the same layer.

Coding the plugin, I came across minor issues related mainly to the `QgsSpatialIndex` implementation. In [the nearest neighbor analysis part]({filename}../2017/qgis-plugin-development-finding-nearest-neighbors.md) of the series, the `QgsSpatialIndex.nearestNeighbor` method was mentioned. Yet, as I found out, this method only works with `QgsPoint` geometries. Those are impossible to get from `QgsPolygon` or `QgsPolyline`, though. What can one possibly do, facing such a misfortune? Well&hellip; draw a solution matrix.

|         | point                           | line                                                                                 | polygon                                                                                 |
|---------|---------------------------------|--------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------|
| **point**   | QgsSpatialIndex.nearestNeighbor | QgsSpatialIndex.nearestNeighbor; layers have to be switched, e.g. source layer = line | QgsSpatialIndex.nearestNeighbor; layers have to be switched, e.g. source layer = polygon |
| **line**    | QgsSpatialIndex.nearestNeighbor | QgsSpatialIndex.intersects with QgsGeometry.distance                                  | QgsSpatialIndex.intersects with QgsGeometry.distance                                     |
| **polygon** | QgsSpatialIndex.nearestNeighbor | QgsSpatialIndex.intersects with QgsGeometry.distance                                  | QgsSpatialIndex.intersects with QgsGeometry.distance                                     |

Using the spatial index brings one more issue I've come to realize just after implementing the special comparison workflows for different geometry types. There's a chance of finding the nearest feature using the bounding box that's actually not the nearest feature. Take a close look at lines number four and seven in the picture below. The first surely is the closest to the polygon on its ride side, yet the polygon is wrongly paired with the line number seven.

<div class="text-center"><img data-echo="/posts/assets/qgis-plugin-development-attribute-transfer-plugin/qgis.png"/></div>

I think the following set of steps will help to overcome this issue:

<ul>
    <li>try using `QgsSpatialIndex.intersects` to find any intersection</li>
    <li>if the intersection is found, get the distance between the target feature and the most distant source vertex</li>
    <li>
        <ul>
            <li>use this distance to construct the new bounding box to test whether there are any closer features</li>
        </ul>
    </li>
    <li>if none is found, grow the target feature bounding box step by step until the intersection is finally found</li>
</ul>

This part is yet to be implemented.
