Title: ogr2ogr UNIX x Windows
Date: 2014-09-23 20:03
Tags: spatial, linux
Category: development

GDAL with its ogr2ogr, ogrinfo and many more is one of the best open source tools to do anything to your spatial data. It is a&nbsp;command line tool, which sort of determines it to be used with UNIX systems, but you might bump into a Windows guy trying to use it as well once in a while.

Be careful, it behaves differently on different OS. Let's say you do something like this on UNIX:

	ogr2ogr -f GeoJSON -where "attribute IN ('value1', 'value2')" output.json input.json

What you <abbr title="But you might get expected result as well">might get is a big nothing</abbr>. Executed on Windows it gives you the result you've expected. *Aargh*, what is that supposed to mean?

Well, that's the ogr2ogr's way to tell you: *Hello there, you need to switch single quotes for double quotes and vice versa, you dumb!* I don't know why and I find it really annoying. Just in case you get stuck with ogr2ogr (or probably any other command line tool), try this.
