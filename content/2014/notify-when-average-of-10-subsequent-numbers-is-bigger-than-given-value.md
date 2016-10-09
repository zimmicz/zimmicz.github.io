Title: Notify When Average of 10 Subsequent Numbers Is Bigger Than Given Value
Date: 2014-09-21 17:38
Tags: php
Category: development

I found an [interesting question](http://stackoverflow.com/questions/25952380/php-find-a-maximum-average-for-10-subsequent-numbers-in-a-list-of-50-random-numb) at StackOverflow asking for help finding solution to what I have already mentioned in the title, with PHP. I gave it a try before reading answers and came up with the following code:

    $avg  = // value we are looking for
    $size = count($numbers);

    for ($i = 0; $i < $size; $i += 1) {
        if ($i + 9 < 51) {
            $val += $numbers[$i];
            for ($j = $i + 1; $j < 10 + $i; $j += 1) {
                $val += $numbers[$j];
            }
            if ($val / 10 >= $avg) { // hit
                // do something
            }
            $val = 0;
        }
    }

That was the first that I could think of. And it worked. The answer given by Dave Chen was much more elegant than my solution (although I think it does something a bit different, but that's not the point here):

    $number = 10; //numbers in a set
    $max = 0;
    $index = 0;

    $size = sizeof($numbers) - $number;
    for ($i = 0; $i < $size; $i++) {
        $tmp = array_sum(array_slice($numbers, $i, $number)) / $number;
        if ($tmp > $max) {
            $max = $tmp;
            $index = $i;
        }
    }

I made a simple benchmark with [`microtime()`](http://php.net/manual/en/function.microtime.php) and found out that my solution (ran 100k times) took about ~12.3 seconds while Dave's took only ~7.4 seconds to finish. That makes his code almost twice faster than mine.

**Lesson learned: do not stop learning!**
