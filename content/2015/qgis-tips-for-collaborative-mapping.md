Title: QGIS Tips For Collaborative Mapping
Date: 2015-07-21 07:51
Category: Tools
Tags: qgis

Right now I'm setting up a project aimed at crop evaluation over ortophotos, HR and VHR imagery. All the steps of evaluation will be done in QGIS with PostGIS used for data storage and post-processing.

In the initial phase, fifteen GIS operators will be using QGIS to reshape geometries and fill attribute data accordingly. Fifteen are not so many, but it is enough to be a possible source of errors. Luckily, there are many things you can do with QGIS to prevent people from making mistakes.

## QGIS project file

QGIS project, the .qgs file, is a pure XML and, unlike ESRI's .mxd, can be edited with any text editor. That's great advantage when you need to prepare one project for many different operators. My project has to load some database layers that should be different for different operators that have different database accounts.

How do you do that? It's enough to create a project using your own credentials and then replace them with `USERNAME` and `PASSWORD` strings as seen below. What happens when the user loads the project?

    :::xml
    <datasource>dbname='database' host=host port=5432 user='USERNAME' password='PASSWORD' sslmode=require key='qgis_id' srid=5514 type=POLYGON table="schema"."table" (wkb_geometry) sql=</datasource>

A popup window will be shown asking him/her to handle bad layers, as QGIS will not be able to connect to the layer. When he/she fills in right credentials (just once), the layer will be loaded. Don't forget to **use a table name that doesn't exist**, QGIS will use the credentials stored with PostGIS connection otherwise and won't ask for them. *I don't like this behaviour.*

Using this multiple times for each user-specific layer is a great time saver.

## Adjust attribute table to fit your needs

QGIS attribute table has so many settings you probably don't use on daily basis and yet they might be invaluable in such project. All of them are available from layer properties under the Fields tab.

<p class='text-center'><img src="{static}/assets/qgis-tips-for-collaborative-mapping/hidden.png" width=50% class="img-responsive centered"></p>

Sadly, our PostGIS layers are very wide in terms of column count. Not all of the columns are to be edited or even seen by operators, so it might be a good idea to hide them by setting their Edit Widget to Hidden. Those that should be seen, but not edited, might be set as not editable by unchecking that option.

Lots of our attributes use enumerations provided by our project partner as CSV files. We use them in QGIS as value maps, so operators don't have to type them manually - we both make their work easier and eliminate mistakes they made.

<p class='text-center'><img src="{static}/assets/qgis-tips-for-collaborative-mapping/valuemap.png" width=50% class="img-responsive centered"></p>

Note QGIS swallows the first row of the given CSV file as if it was a header. Don't forget about this when creating your own enumerations. Once set, operators will see a friendly combo box instead of a hostile blank input in the attribute table.

These are just small adjustments that can make a big difference in your QGIS workflow.
