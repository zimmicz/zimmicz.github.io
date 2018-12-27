Title: GRASS: Big Buffers Made Easy
Date: 2015-04-20 21:06
Tags: grass
Category: automation

Recently I've written about [struggling with fairly complex geometries in PostGIS]({filename}/2015/postgis-buffers-intersections-differences-and-collections.md). Lesson learned from the last time was to use more smaller geometries instead of several really huge. You can obtain the small ones from the big by [cutting it with a grid]({filename}/2015/postgis-rectangular-grid-creation.md).

A supervisor of a project I've been working on came up with a task that totally buried the previous process in a blink of an eye: **Give me the buffer (diffed with original geometries) that is smoothed on the outer bounds so there are no edges shorter than 10 cm.** I sighed. Then, I cursed. Then, I gave it a try with PostGIS. Achieving this goal involves these steps:

* Dissolve intersecting buffers
* Run some kind of generalization algorithm that is not defined in PostGIS
* Diff original geometries
* Cut buffer with grid so it is <del>faster</del> not so slow for the next steps

Two of those four are rather problematic with PostGIS: line smoothing and diffing the original geometries (I didn't get to the last one, so it might be 3 of 4 as well).

## Hello, I'm GRASS

I haven't used GRASS for ages and even back then I didn't get to know it much, but it saved the day for me this time.

    :::bash
    grass -text path/to/mapset -c

    v.in.ogr input="PG:host=localhost dbname=db user=postgres password=postgres" output=ilot_050 layer=ilot_2015_050 snap=-1 --overwrite
    # turn the snapping off, I don't want the input changed in any way, even though it is not topologically valid
    v.in.ogr input="PG:host=localhost dbname=db user=postgres password=postgres" output=lollipops_050 layer=lollipops.lollipops_2015_050_tmp snap=-1 --overwrite
    v.in.ogr input="PG:host=localhost dbname=db user=postgres password=postgres" output=holes_050 layer=phase_3.holes_050 snap=-1 --overwrite
    v.db.addcolumn map=ilot_050 columns="id_0 int"
    v.db.update map=ilot_050 column=id_0 value=1

    # dissolve didn't work without a column specified, dunno why
    v.dissolve input=ilot_050 column=id_0 output=ilot_050_dissolve --overwrite
    v.buffer input=ilot_050_dissolve output=ilot_050_buffer distance=20 --overwrite

    # v.out and v.in routine used just because I didn't get the way attributes work in GRASS, would do it differently next time
    v.out.ogr input=ilot_050_buffer output=ilot_050_buffer format=ESRI_Shapefile --overwrite
    v.in.ogr input=ilot_050_buffer output=ilot_050_buffer snap=-1 --overwrite
    v.overlay ainput=ilot_050_buffer binput=holes_050 operator=or output=combined_050_01 snap=-1 --overwrite

    # tried v.patch to combine the three layers, it gave some strange results in the final overlay
    v.overlay ainput=combined_050_01 binput=lollipops_050 operator=or output=combined_050_02 snap=-1 --overwrite
    v.out.ogr input=combined_050_02 output=combined_050 format=ESRI_Shapefile --overwrite
    v.in.ogr input=combined_050 output=combined_050_in snap=-1 --overwrite
    v.db.addcolumn map=combined_050_in columns="id_1 int"
    v.db.update map=combined_050_in column=id_1 value=1
    v.dissolve input=combined_050_in column=id_1 output=combined_050_dissolve --overwrite

    # get rid of < 10cm edges
    v.generalize input=combined_050_dissolve output=combined_050_gen method=reduction threshold=0.1 --overwrite
    v.out.ogr input=combined_050_gen output=combined_050_gen format=ESRI_Shapefile --overwrite
    v.in.ogr input=combined_050_gen output=combined_050_gen snap=-1 --overwrite
    v.overlay ainput=combined_050_gen binput=ilot_050 operator=not snap=1e-05 --overwrite output=ilot_050_diff
    v.out.postgis input=ilot_050_diff output="PG:dbname=db user=postgres password=postgres" output_layer=onf3.buffer_050_diff options="GEOMETRY_NAME=wkb_geometry,SRID=2154" --overwrite
    v.in.ogr input="PG:host=localhost dbname=ign user=postgres password=postgres" output=buffer_050 layer=onf3.buffer_050_diff snap=-1 --overwrite
    v.in.ogr input="PG:host=localhost dbname=ign user=postgres password=postgres" output=grid layer=grid snap=-1 --overwrite
    v.db.connect -d map=buffer_050

    # instead of v.out and v.in routine
    db.connect driver=sqlite database='$GISDBASE/$LOCATION_NAME/$MAPSET/sqlite.db'
    v.db.addtable map=buffer_050
    v.overlay ainput=buffer_050 binput=grid operator=and output=buffer_050_grid snap=-1 --overwrite
    v.out.postgis input=buffer_050_grid output="PG:dbname=ign user=postgres password=postgres" output_layer=onf3.buffer_050_diff_grid options="GEOMETRY_NAME=wkb_geometry,SRID=2154" --overwrite

**It is damn fast** compared to PostGIS. It can be automated. It can be parametrized. It is robust. It is great!

## Lesson learned

* You cannot smooth lines by deleting edges shorter than `n` in PostGIS. At least I haven't found the way to do so without defining your own procedure. You can with GRASS.
* GRASS reduction algorithm always keep first and last node untouched. Thus, if they're closer than `n`, they'll stay even if you'd like to have them deleted.
* Getting to grips with GRASS attribute data is rather hard after using shapefiles all your GIS life.
* It is great to exploit synergy of different GIS tools used for what they're best at.

The more I work with big data, the more I get used to not seeing them. That's kind of a twist after crafting maps at university.
