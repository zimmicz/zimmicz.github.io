Title: Degrees To Decimal With Javascript
Date: 2014-09-09 20:28
Category: development
Tags: javascript

I have found a nice way to get decimal value from degrees of longitude and latitude recently:

	:::javascript
	function format(coords) {
	    var decimal = 0,
	        output  = [],
	        coords  = coords.split('  '); // it might be <br> as well

	    for (var i = 0; i < coords.length; i += 1) {
	        var c = coords[i].split(' ');

	        for (var j = 0; j < c.length; j += 1) {
	            decimal += c[j] / Math.pow(60, j);
	        }

	        output.push(parseFloat(decimal).toFixed(5));
	        decimal = 0;
	    }

	    prompt('Souřadnice bodu', output.join(', '));
	}

When you call `format("DD° MM' SS'  DD° MM' SS'");` you'll get decimal value in return (or `prompt` to be accurate). What I like the most about this solution is the usage of Math.pow(). I think it is a neat way to transform the values as you need to divide parts of latitude or longitude by 60<sup>0</sup>, 60<sup>1</sup> and 60<sup>2</sup> respectively.

There is definitely a googol of different solutions to this task, I just liked the simplicity of this one.
