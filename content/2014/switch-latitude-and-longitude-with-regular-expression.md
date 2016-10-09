Title: Switch Latitude And Longitude With Regular Expression
Date:  2014-09-14 17:21
Category: development
Tags: sublime, regex

It happens that you receive a file with longitude and latitude just in the opposite order that you would like to have. It's fairly easy to switch those without loading it into Excel or Calc and doing `Ctrl + C` and `Ctrl + V` on columns.

If you have a file with tabular data that looks like this:

	 50.52, 60.15
	 70.96, 80.1
	-55.23, 62.03

You can use Sublime Text to switch the values:

1. Press `Ctrl + H`
2. Copy `(\-?\d+\.?\d+),?[\t ]*(\-?\d+\.?\d+)$` to *Find What* input
3. Copy `$2,$1` to *Replace With* input

Hit *Replace All* button and you're done.
