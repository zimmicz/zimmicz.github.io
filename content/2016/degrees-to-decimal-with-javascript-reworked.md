Title: Degrees To Decimal With Javascript Reworked
Date: 2016-10-28 16:00
Category: development
Tags: javascript

Two years ago I was pretty happy with [this little piece of code to transform degrees to the decimal value](https://www.zimmi.cz/posts/2014/degrees-to-decimal-with-javascript/). Yesterday, I found a neater way to do the same:

	:::javascript
	let deg = [50, 30, 0];

	function degToDec(prev, cur, curIndex) {
    	return prev + cur / Math.pow(60, curIndex);
	}

	deg.reduce(degToDec);

Once you have an input array, that's pretty much it. Love JavaScript.
