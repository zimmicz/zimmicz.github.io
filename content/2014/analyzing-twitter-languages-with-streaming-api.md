Title: Analyzing Twitter Languages With Streaming API
Date: 2014-09-02 17:37
Tags: javascript, leaflet, twitter
Category: development

<p>I am writing a diploma thesis focused on extracting spatial data from social networks. I have been working mainly with Twitter API and results I have got so far look really promising. This post was written as a reaction to many retweets I got when I shared one of my visualizations. It aims to make it clear how to connect to Twitter Streaming API using <a href="http://nodejs.org/">node.js</a>, <a href="http://leafletjs.com/">Leaflet</a> and <a href="http://sqlite.org/">SQLite</a> and retrieve tweets to analyze them later.</p>

<p>If you have any further questions after reading this paper, feel free to contact me via <a href="https://twitter.com/zimmicz">Twitter</a> or <a href="mailto:zimmicz@gmail.com">e-mail</a>. I must say right here <strong>that the code will be shared as well as the map</strong>, but there are still some bugs/features I would like to remove/add.</p>

<p><small>On a side note: I have been studying cartography and GIS for the last five years at Masaryk University in Brno, Czech Republic. I am mostly interested in ways computers can make data handling easier. I&nbsp;like to code in Python.</small></p>

<h3>Using Twitter Streaming API</h3>

<p>As you probably know, Twitter offers three different APIs:</p>

<ul>
<li>REST API which is obviously RESTful. You can access almost every piece of information on Twitter with this one: tweets, users, places, retweets, followers&#8230;</li>
<li>Search API used for getting search results. You can customize these by sending parameters with your requests.</li>
<li><strong>Streaming API</strong> which I am going to tell you about. It is really different, as (again, obviously) it keeps streaming tweets from the time you connect to the server. This means, once the connection is made, it has to stay open as long as you want tweets coming to you. The important thing here is that you get real time tweets delivered to you via this <abbr title="Twitter only delivers a sample of tweets, not the whole traffic.">stream</abbr>, which implies you cannot use this API to get tweets already tweeted.</li>
</ul>

<p><strong>To sum it up: You get a small sample of tweets in a real time as long as the connection to the server stays open.</strong></p>

<h3>What you need</h3>

<p>To use any of the Twitter APIs, you need to authenticate you (or your app) against Twitter via OAuth protocol. To be able to do so, you need a Twitter account, because only then you can <a href="https://dev.twitter.com/">create apps</a>, obtain access tokens and get authenticated for API use.</p>

<p>And then, obviously, you need something to connect to server with. I chose <strong>node.js</strong> because it seemed as a good tool to keep connection alive. I have also been interested in this technology for the couple of months but never really had a task to use it for.</p>

<p>The good thing about node.js is that it comes with lots of handy libraries. You get <strong>socket.io</strong> for streaming, <strong>ntwitter</strong> for using Twitter API and <strong>sqlite3</strong> for working with SQLite databases.</p>

<p>You need something to store the data in also. As mentioned, I picked SQLite for this task. It is lightweight, does not need server nor configuration to run, just what I was looking for. Seems we are set to go, right?</p>

<h3>Filtering the data</h3>

<p>I guess none of you is interested in obtaining random tweets from around the world, neither was I. I live in the Czech republic and that is the area I want to get tweets from. How?</p>

<p>It is fairly simple, you tell Twitter with the <code>locations</code> parameter of <a href="https://dev.twitter.com/docs/api/1.1/post/statuses/filter"><code>statuses/filter</code></a> resource. This parameter specifies a set of bounding boxes to track.</p>

<p><strong>To sum it up: you connect to the server and tell it you just want to get tweets from the area you specified with the <code>locations</code> parameter. The server understands and keeps you posted.</strong></p>

<h4>Is it that simple?</h4>

<p>No. Twitter decides whether to post you the tweet or not according to what the value of coordinates field is. It goes like this:</p>

<ol>
<li>If the <code>coordinates</code> field is not empty, it gets tested against the bounding box. If it matches, it is sent to the stream.</li>
<li>If the <code>coordinates</code> field is empty, but the <code>place</code> field is not, it is the <code>place</code> field that gets checked. If if it by any extent intersects the bounding box, it is sent to the stream.</li>
<li>If both of the fields are empty, nothing is sent.</li>
</ol>

<p>I decided to throw away the tweets with the empty <code>coordinates</code> field, because the accuracy of the value specified in the place field can be generally considered very low and insufficient for my purposes. You still need to account for position inaccuracies of users&#8217; devices though, however that is not something that we can deal with. <em>Let us just assume that geotagged tweets are accurate.</em></p>

<div class="text-center"><img src="/posts/assets/analyzing-twitter-languages-with-streaming-api/cr.png" width="50%" height="50%" title="Geotagged tweets" class="img-rounded"><p><strong>Figure:</strong> Twitter seems not to be very accurate when matching tweets against bounding box.</p></div>

<p>Although, as you can see in the picture, they are not. Or they are, but Twitter is not good at telling so. Besides that, none of the countries in the world is shaped like a rectangle and we would need to clip the data anyway. That is where SQLite comes in, because I have been saving incoming tweets right into the database.</p>

<p>If you use any GUI manager (sqlitebrowser for Linux is just fine), you can easily export your data to the CSV file, load it into QGIS, clip it with Natural Earth countries shapefile and save them to the GeoJSON file. It is just a matter of few JavaScript lines of code to put GeoJSON on a Leaflet map.</p>

<h3>Displaying the data</h3>

<p>Once a GeoJSON file is ready, it can be used for making an appealing viz to get a sense of what may be called &#8220;nationalities spatial patterns&#8221;. The <code>lang</code> field (stored in the database, remember?) of every tweet is used to colour the marker accordingly. Its value represents a two-letter language code as specified in ISO 639-1 document.</p>

<p>However, as those codes are guessed by Twitter&#8217;s language algorithms, they are prone to error. There are actually three scenarios we might be facing:</p>

<ol>
<li>User tweets in the same language as used in the Twitter account.</li>
<li>User tweets in his/her mother language, but has set different Twitter account language.</li>
<li>User does not tweet in his/her mother language, but has it set as a Twitter account language.</li>
</ol>

<p>We basically have to deal with 2) and 3), because 1) means we can be pretty sure what nationality the user is. Sadly though, I have not found an easy way to tell which one of these two we came across, thus which language settings should be prioritized. I made an arbitrary decision to prioritize the language the tweet was written in, based on assumption that <strong>the most of the users tweet in their mother language</strong>. No matter what you do, the data is still going to be biased by automatically generated tweets, especially ones sent by Foursquare saying &#8220;I&#8217;m at @WhateverBarItIs (http://someurl.co)&#8221;. It works fine for the strange languages like Russian and Arabic though.</p>

<p>From Jan 2 to Jan 4 this year 5,090 tweets were collected. Leaflet is becoming a little sluggish without clustering turned on displaying all of them. Plans are to let the collection run until Jan 7 and then put all the tweets on the map. I guess that might be around 10,000 geotagged tweets by that time.</p>

<p>I am definitely willing to share the <abbr title="Do not expect much, it was my first time with node.js">code</abbr> and the final viz. Meanwhile, you can have a look at the screenshot on picture [*]. I have already implemented nationality switch (legend items are clickable) and I would like to add a day/night switch to see whether there are any differences between the peoples&#8217; behaviour. </p>

<div class="text-center"><img width="60%" height="60%" src="/posts/assets/analyzing-twitter-languages-with-streaming-api/screenshot.png" title="Final geoviz using Leaflet" class="img-rounded"><p><strong>Figure:</strong> Final map screenshot. A legend is used to turn nationalities on and off. You are looking at Prague by the way.</p></div>

<p>Obviously the most tweets were sent from the most populated places, e.g. Prague, Brno, Ostrava. </p>
