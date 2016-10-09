Title: Color Relief Shaded Map Using Open Data with Open Source Software
Date: 2015-10-25 09:42
Tags: bash, gdal, linux, qgis
Category: automation

The Digital Elevation Model over Europe (EU-DEM) has been recently released for public usage at [Copernicus Land Monitoring Services homepage](http://land.copernicus.eu/in-situ/eu-dem). Strictly speaking, it is a **digital surface model** coming from weighted average of SRTM and ASTER GDEM with geographic accuracy of 25 m. Data are provided as GeoTIFF files projected in 1 degree by 1 degree tiles (projected to EPSG:3035), so they correspond to the SRTM naming convention.

If you can't see the map to choose the data to download, make sure you're not using HTTPS Everywhere or similar browser plugin.

I chose **Austria** to play with the data.

## Obtaining the data

It's so easy I doubt it's even worth a word. Get zipped data with `wget`, extract them to a directory.

    :::bash
    wget https://cws-download.eea.europa.eu/in-situ/eudem/eu-dem/EUD_CP-DEMS_4500025000-AA.rar -O dem.rar
    unrar dem.rar -d copernicus
    cd copernicus

## Hillshade and color relief

Use GDAL to create hillshade with a simple command. No need to use `-s` flag to convert units, it already comes in meters. Exaggerate heights a bit with `-z` flag.

    :::bash
    gdaldem hillshade EUD_CP-DEMS_4500025000-AA.tif hillshade.tif -z 3

And here comes the Alps.

<p class="text-center"><img title="Hillshade" src="{filename}/assets/color-relief-shaded-map-using-open-data-and-open-source-software/hillshade.png" class="center"></p>

To create a color relief you need a ramp of heights with colors. ["The Development and Rationale of Cross-blended Hypsometric Tints"](http://cartographicperspectives.org/index.php/journal/article/viewFile/20/70) by T. Patterson and B. Jenny is a great read on **hypsometric tints**. They also give advice on what colors to choose in different environments (see the table at the last page of the article). I settled for warm humid color values.

<table class="center">
<thead>
    <tr>
        <th>Elevation [m]</th>
        <th>Red</th>
        <th>Green</th>
        <th>Blue</th>
    </tr>
</thead>
<tbody>
<tr style="background: rgb(220, 220, 220)">
<td>5000</td>
<td>220</td>
<td>220</td>
<td>220</td>
</tr>
<tr style="background: rgb(212, 207, 204)">
<td>4000</td>
<td>212</td>
<td>207</td>
<td>204</td>
</tr>
<tr style="background: rgb(212, 193, 179)">
<td>3000</td>
<td>212</td>
<td>193</td>
<td>179</td>
</tr>
<tr style="background: rgb(212, 184, 163)">
<td>2000</td>
<td>212</td>
<td>184</td>
<td>163</td>
</tr>
<tr style="background: rgb(212, 201, 180)">
<td>1000</td>
<td>212</td>
<td>201</td>
<td>180</td>
</tr>
<tr style="background: rgb(196, 192, 166)">
<td>600</td>
<td>169</td>
<td>192</td>
<td>166</td>
</tr>
<tr style="background: rgb(134, 184, 159)">
<td>200</td>
<td>134</td>
<td>184</td>
<td>159</td>
</tr>
<tr style="background: rgb(120, 172, 149)">
<td>50</td>
<td>120</td>
<td>172</td>
<td>149</td>
</tr>
<tr style="background: rgb(114, 164, 141)">
<td>0</td>
<td>114</td>
<td>164</td>
<td>141</td>
</tr>
</tbody>
</table>

I created a color relief with another GDAL command.

    :::bash
    gdaldem color-relief EUD_CP-DEMS_4500025000-AA.tif ramp_humid.txt color_relief.tif

And here comes hypsometric tints.

<p class="text-center"><img title="Color relief" src="{filename}/assets/color-relief-shaded-map-using-open-data-and-open-source-software/color_relief.png" class="center"></p>

Add a bit of compression and some overviews to make it smaller and load faster.

    :::bash
    gdal_translate -of GTiff -co TILED=YES -co COMPRESS=DEFLATE color_relief.tif color_relief.compress.tif
    gdal_translate -of GTiff -co TILED=YES -co COMPRESS=DEFLATE hillshade.tif hillshade.compress.tif
    rm color_relief.tif
    rm hillshade.tif
    mv color_relief.compress.tif color_relief.tif
    mv hillshade.compress.tif hillshade.tif
    gdaladdo color_relief.tif 2 4 8 16
    gdaladdo hillshade.tif 2 4 8 16

## Map composition

I chose Austria for its excessive amount of freely available datasets. What I didn't take into consideration was my lack of knowledge when it comes to German (#fail). States come from [data.gv.at](http://data.gv.at) and was dissolved from smaller administrative units. State capitals were downloaded from [naturalearth.com](http://naturalearth.com).

<p class="text-center"><a href="{filename}/assets/color-relief-shaded-map-using-open-data-and-open-source-software/map.pdf" title="Click for PDF version"><img title="Austria" src="{filename}/assets/color-relief-shaded-map-using-open-data-and-open-source-software/map.png" class="center"></a></p>

I'd like to add some more thematic layers in the future. And translate the map to English.

## Few words on INSPIRE Geoportal

[INSPIRE Geoportal](http://inspire-geoportal.ec.europa.eu/) should be the first place you go to search for European spatial data (at last EU thinks so). I used it to find data for this map and it was a very frustrating experience. It was actually more frustrating than using Austrian open data portal in German. Last news are from May 21, 2015, but the whole site looks and feels like deep 90s or early 2000 at least.