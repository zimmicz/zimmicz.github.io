Title: Hosting Website On Openshift
Date: 2015-02-23 14:25
Tags: openshift
Category: development

I decided to migrate [my web](http://www.zimmi.cz) to [OpenShift](http://openshift.com). It was a bit frustrating but I got it working eventually.

## Things to know before taking the leap

Some domain providers don't support CNAME changes for root domains (zimmi.cz in my case). This means you can't simply tell your domain to serve content from OpenShift address. But what you can do is to tell your `www` subdomain to do so:

    www.zimmi.cz CNAME hp-zimmi.rhcloud.com

Which is great until you realize you've just created two different websites. That's where [wwwizer](http://wwwizer.com/) lends you a hand and lets you redirect your naked domain to your `www` domain:

    zimmi.cz A 174.129.25.170

Now everything works fine and you have your `www.domain.tld` up and running.

## OpenShift subdomains

I wasn't successful creating a subdomain on the same application where I run my domain. This can be easily solved by creating another application and pointing DNS to it:

    posts.zimmi.cz A 174.179.25.170
    www.posts.zimmi.cz CNAME posts-zimmi.rhcloud.com

Just don't forget to handle both naked and `www` version. When Google reindexes new URLs (http://www.zimmi.cz/posts instead of http://posts.zimmi.cz) subdomain application might be deleted.
