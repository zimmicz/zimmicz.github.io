Title: Migrating Geoserver And Checking For Missing Data
Date: 2014-10-29 16:25
Tags: geoserver,python
Category: development

I've upgraded a handful of Geoserver installations and it has never been flawless. If you're lucky you end up with just *some* layers missing, if you're not, you'll miss a bunch of them (together with layergroups, some stores, workspaces might screw up etc.).

But how do you check for missing data before switching to the newer version? Thanks to the [REST API implemented within Geoserver](http://docs.geoserver.org/stable/en/user/rest/api/index.html), it's rather easy.

    import requests
    from bs4 import BeautifulSoup
    from requests.auth import HTTPBasicAuth

    req = requests.get('http://example.com/geoserver/rest/layers', auth=HTTPBasicAuth('username', 'password'))

    html = BeautifulSoup(req.text)
    i = 0
    for link in html.find_all('a'):
        i += 1
        href = link.get_text()
        print i

    with open('list.txt', 'a') as f:
            f.write(href)
            f.write('\n')

We needed to migrate ~ 17,000 layers last week, and yes, we could have just shut the door and spend couple of nights checking one after another, if we were the dumbest GIS company ever.

As I wanted to make it a bit easier I wrote the simple Python script (see above) that just authenticates against Geoserver and downloads the list of layers. I actually had to do that twice - both old and new instance. A [simple file comparison](https://www.diffchecker.com/) followed and I got a list of missing layers in less than two minutes.

If you do the same to workspaces, stores and layergroups, your chances of not losing some data after the switch are pretty high.

I guess it's reasonable to check your maps by hand as well, but this gives you the picture of the current state of your data real quick.
