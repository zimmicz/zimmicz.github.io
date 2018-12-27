Title: WMTS: Few Things I Want To Remember
Date: 2014-09-10 20:36
Category: web maps
Tags: ogc, wmts

- Used to serve prepared rectangular tiles; this means you are limited by web server speed rather than map server speed
- Several ways to retrieve tiles are defined: KVP and REST are mandatory, SOAP is optional
- Does not allow layer combination; additional tile matrix would have to be created
- GetCapabilities, GetTile and GetFeatureInfo requests are defined
- **tile**
  - rectangular representation of space
  - defined by tile and row indices
- **tile matrix**
  - set of tiles for a given scale
  - *defined with:*
    - tile size derived from standardized pixel size (0.28 &times; 0.28 mm)
    - tile width and tile height (px)
    - left upper corner coordinates
    - matrix width and height as number of tiles
- **tile matrix set**
  - set of tile matrices for different scales

### Total count of tile matrices

*`nTileMatrices × nTiledStyles × nTiledFormats (if no dimensions are defined)`*

### Total count of tiles in a tile matrix
*`matrixWidth × matrixHeight`*

### Other equations
- <code>pixelSpan = scaleDenominator × 0.28 10<sup>3</sup> / metersPerUnit(crs);</code>
- <code>tileSpanX = tileWidth × pixelSpan;</code>
- <code>tileSpanY = tileHeight × pixelSpan;</code>
- <code>tileMatrixMaxX = tileMatrixMinX + tileSpanX × matrixWidth;</code>
- <code>tileMatrixMinY = tileMatrixMaxY - tileSpanY × matrixHeight;</code>

<img src="{static}/assets/wmts-few-things-i-want-to-remember/wmts.png" title="WMTS tiling schema" class="img-responsive centered">
