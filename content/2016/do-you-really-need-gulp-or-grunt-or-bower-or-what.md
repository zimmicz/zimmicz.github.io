Title: Do You Really Need Gulp? Or Grunt? Or Bower? Or What?
Date: 2016-3-20 19:15
Tags: javascript
Category: development

**Disclaimer:** I'm an enthuastic developer, but I do not code for a living. I'm just the ordinary guy who keeps editing a wrong file wondering why *the heck* the changes are not being applied.

**TL;DR:** I do think `npm` might be the answer.

## Wonderful world of JavaScript DevOps
When I first started using JavaScript on the server side with `node.js`, I felt overwhelmed by numerous options to automate tasks. There was `npm` taking care of backend dependencies. Then I would build a&nbsp;frontend and found out about `bower` for handling frontend dependencies. Then it would be great to have some kind of minification/obfuscation/uglification/you-name-it task. And the `build` task. And the `build:prod` task. And how about `eslint` task? And then I would end up spending hours doing nothing, just reading blogs about the tools being used by others who do code for a living.

**Intermezzo:** I think my coding is slow. Definitely slower than yours. I'm getting better though.

## Using the force
Looking back I find it a bit stressful - how *the heck* do I choose the right tools? Where's Yoda to help me out? Anyway, next to adopt after `npm` was `bower`. And I liked it, even though some packages were missing - but who cares as long as there is no better way, right? Except there is&hellip; I guess.

Automation was next in the line to tackle. So I chose `gulp` without a bit of hesitation. It was a&nbsp;hype, a bigger than `grunt` back then. I even heard of `yeoman`, but until now I still don't know what it actually does. And I'm happy with that.

A short summary so far:

* `npm` for backend dependencies
* `bower` for frontend dependencies
* `gulp` for running tasks

So far, so good.

## Is Bower going to die?
Then I stumbled upon this tweet and started panicking. Or rather started to feel cheated. *It took me time to set all this up and now it's useless? Or what?*

<blockquote class="twitter-tweet" data-lang="en"><p lang="en" dir="ltr">Bower development is stopped. Move to npm, if you haven&#39;t already. <a href="https://t.co/RQRcE7DT5V">https://t.co/RQRcE7DT5V</a></p>&mdash; Nacho Coloma (@nachocoloma) <a href="https://twitter.com/nachocoloma/status/663622545162280960">November 9, 2015</a></blockquote>
<script async src="//platform.twitter.com/widgets.js" charset="utf-8"></script>

Seeing it now, I'm glad I read this. And I really don't know what happened to Bower, if anything at all.

## Keeping it simple
So Bower's dying, what are you going to do about that? You'll use `npm` instead! And you'll have a&nbsp;single source of truth called `package.json`. You'l resolve all the dependencies with a single `npm install` command and feel like a king. We're down to two now - `npm` and `gulp`.

##Gulp, Gulp everywhere!
When you get rid of Bower, next feeling you have is your `gulpfile.js` just got off the leash. It got really big and grew to ~160 lines of code and became a nightmare to manage.

So you split it into [task files](https://github.com/zimmicz/bookmap/commit/98a3ce451856e2beaac8fa2be9eb3b7e2878b0a7) and a [config file](https://github.com/zimmicz/bookmap/commit/07eaf7d355a47ff9d08e5b7138791a67669534d6). What a relief. But you still realize a **half** of your `package.json` dependencies starts with `gulp-`. And you hate it.

##Webpack for the win
For me, a non-developer, setting the [webpack](https://webpack.github.io/) wasn't easy. I didn't find docs very helpful either. Reading the website for the first time, I didn't even understand what it should be used for. I&nbsp;got it working eventually. And I got rid of `gulp`, `gulp-connect`, `gulp-less`, `gulp-nodemon`, `gulp-rename`, `gulp-replace`, `gulp-task-listing` and `gutil`. And the whole `gulpfile.js`. That was a big win for me.

##But how do you run tasks?
Well&hellip;
    
    :::bash
    npm run start-dev # which in turn calls the code below
    npm run start-webpack & NODE_ENV=development nodemon server.js # where start-webpack does the following
    node_modules/webpack-dev-server/bin/webpack-dev-server.js --quiet --inline --hot --watch

That's it. If I need to build code, I run `npm run build`, which calls some other tasks from `scripts` section in the `package.json`.

That's pretty much it. I don't think it's a silver bullet, but I feel like I finally found peace of mind for my future JavaScript development. At least for a month or so before some other guy comes to town.