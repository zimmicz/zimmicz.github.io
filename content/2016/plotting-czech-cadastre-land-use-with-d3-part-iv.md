Title: Plotting the Czech Cadastre Land Use with d3: Data Viz (part IV)
Date: 2016-11-20 14:45
Category: data
Tags: d3, javascript, svg

This post is the fourth part of the series summarizing the process of visualizing land use data with bash, PostgreSQL and d3.js. Read other parts:

1. [Plotting the Czech Cadastre Land Use with d3: Data Extraction (part I)]({filename}../2016/plotting-czech-cadastre-land-use-with-d3-part-i.md)
2. [Plotting the Czech Cadastre Land Use with d3: Data Transformation (part II)]({filename}../2016/plotting-czech-cadastre-land-use-with-d3-part-ii.md)
3. [Plotting the Czech Cadastre Land Use with d3: Data Load (part III)]({filename}../2016/plotting-czech-cadastre-land-use-with-d3-part-iii.md)

## Data vizualization

Those of you who've been following this series know all the data are set and ready to be used. The rest of you, _shame on you by the way_, can go through the above posts to catch up.

The result is available at [https://www.zimmi.cz/kn-landuse-monitor](https://www.zimmi.cz/kn-landuse-monitor) and works like the gif below.

<div class="text-center"><img data-echo="/posts/assets/plotting-the-czech-cadastre-land-use-with-d3-part-iv/screen.gif" /></div>

### Features

- land use data for 13,093 cadastral areas between 2015/01/01 and 2016/10/01
- relative area and parcel count per land use type
- similar cadastres based on land use relative area values
- time series plots for various charachteristics (including agricultural land area and parcel count)

### Todos

- time series chart titles onmouseover
- barchart titles onmouseover
- absolute values chart (?)
- `fetch API` polyfill
- Firefox seems to be broken

### Technologies

I implemented [the whole app with vanilla JavaScript](https://github.com/zimmicz/kn-landuse-monitor/tree/f0af50d44d6aac11adb6cdb0c7c67a97d7db1df3). The app resided in the `Monitor` variable, had several modules that were communicating via custom events with each other.

So far, so good. Once the app was production-ready, I stumbled upon [vue.js](https://vuejs.org), which is by miles the best JavaScript framework experience I've had so far. Reinventing the app once again was the matter of two days (thanks to [this amazing setup](https://github.com/vuejs-templates/webpack) - hot reload included).

Thus, the current version of the app is based on:

#### vue.js
Thanks to the easy-to-understand system of components, properties and methods, learning curve is really steep. The app is now divided into several components (Search, Dashboard with child components for charts and similar cadastres list).

#### vuex
[Vuex](https://vuex.vuejs.org/en/), probably inspired by Flux or Redux, is the _"state management pattern + library"_, the single source of truth for your apps. That's pretty much it: there's only one place in your app (called the `store`), where you go to put or get your data. Not necessarily every single piece of data, just those pieces used across several components. It plays really nice with the vue.js.

#### D3.js
Tried it before, [D3.js](https://d3js.org) was really hard to grasp. And it still is, I guess. At the same time, it's damn good at plotting the data. Yet, being a bit less low-level would be great.

#### Dexie
I hate writing servers for my pet projects. The server means no Github Pages. Thus, I decided to load the whole dataset with `fetch API`  from the external JSON file. Loading the 13K objects &times; 30 properties &times; array with 8 items in each didn't seem like the best idea ever, so&hellip; Here comes [Dexie](http://dexie.org), a `IndexedDB API` wrapper that makes it easy on you (unlike the `IndexedDB API` itself, which doesn't even let you find out whether the database you're creating already exists. Seriously?).

Dexie loads the initial dataset into the IndexedDB storage and reads it every time user comes back without loading the JSON file again. On data change, the fresh file will be loaded, the database flushed and the new data written. [Behold](https://github.com/zimmicz/kn-landuse-monitor/blob/master/src/stores/actions.js); I hate the way it's written.

#### Flex
Used `flex` for the first time, I'm not sure I understand how it actually works though. CSS feels more complicated every time I need it.

<small>Bottom line: I use localStorage to keep track of the database existence.</small>

### Resume

Two pet projects completed in one month definitely means the winter is here! Looking forward to using more vue.js.