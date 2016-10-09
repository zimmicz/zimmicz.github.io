Title: Geoserver Printing With Mapfish
Date: 2014-09-02 17:41
Tags: geoserver
Category: development

<p>Printing a web map requires a lot more than doing <code>Ctrl + P</code>. <a href="http://mapfish.org/">MapFish</a> seems to be the best option to use with Geoserver, and it comes <a href="http://docs.geoserver.org/stable/en/user/community/printing/">ready as an extension</a>. If you installed the module properly, you should be seeing general info at <a href="http://localhost:8080/geoserver/pdf/info.json">http://localhost:8080/geoserver/pdf/info.json</a>. You&#8217;ll find a <code>config.yaml</code> in <code>data_dir/printing</code>.</p>

<p>MapFish lets you access three different points:</p>

<ol>
<li><code>info.json</code> that returns current config as defined in config.yaml file</li>
<li><code>print.pdf</code> that actually prints the map as defined in the <code>spec</code> GET argument</li>
<li><code>create.json</code> that returns a JSON object with an URL of the printed map</li>
</ol>

<p>Remember, if you&#8217;re displaying a lot of layers in the map and all of them should be printed, you need to pass it as a POST argument when calling <code>print.pdf</code> or <code>create.json</code>, otherwise you&#8217;ll be getting an error complaining about the GET request length.</p>

<p>The <code>config.yaml</code> file is where you define settings for the print module. You definitely want to define <code>dpis</code> (we&#8217;re using 90, 200 and 300 DPI), <code>scales</code> (they probably need to be hardcoded, I didn&#8217;t succeed trying any arbitrary scale) and <code>layouts</code> (we&#8217;re using A4 to A0 both portrait and landscape).</p>

<p>However, defining the page size might get tricky as MapFish does not use standardized sizes defined in cm, in or any other unit. I&#8217;ve experimenting and doing some maths and here&#8217;s what I came up with for portrait layouts.</p>

<table class="table-centered">
    <tr>
        <th>A0</th>
        <th>A1</th>
        <th>A2</th>
        <th>A3</th>
        <th>A4</th>
    </tr>
    <tr>
        <td>2382&times;3361</td>
        <td>1683&times;2380</td>
        <td>1190&times;1680</td>
        <td>840&times;1180</td>
        <td>595&times;832</td>
    </tr>
</table>

<p><em>The bigger paper you use, the smaller DPI is available</em>, that&#8217;s what I found out messing around with MapFish settings. This means that we&#8217;re using 200 DPI top for A2 layout and 90 DPI for A1 and A0 layout, respectively.</p>

<p>JQuery takes care of sending POST request and fetching the response. <a href="http://www.edpp.cz/poli_mapa-povodnoveho-planu-mesta/">See it in action</a> (Choose <em>Nástroje</em> and <em>Tisknout</em> for printing).</p>
