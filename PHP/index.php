<?php
    /**********************************************************************
     * Redmond Kettle Control
     * PHP wrapper for python script
     * (c) Boris Emchenko 2020
     * based on https://habr.com/ru/post/412583/ and https://habr.com/en/post/371965/ 
     * 
     * ToDo:
     * - return refresh date  in json object
     * - set mode (boling/heating)
     * - return other data (kettle version)
     * 
     * History:
     * 
     * v1.1 [2020/03/16] all goes to json
     * v1.1 [2020/03/10] json refresh command
     * v1.0 [2020/03/09] on, off, test (refresh) command
     *
    ***********************************************************************/
    $command = $_GET["cmd"];
    $rnd=rand (10000,99999);
    if (!($command > 0)):
?>
<a href=?cmd=1&sid=<?php print $rnd;?>>ON</a><br>
<a href=?cmd=2&sid=<?php print $rnd;?>>OFF</a><br>
<a href=?cmd=3&sid=<?php print $rnd;?>>REFRESH (verbose) - obsolete</a><br>
<a href=?cmd=4&sid=<?php print $rnd;?>>REFRESH (JSON)</a><br>
<a href=?cmd=5&sid=<?php print $rnd;?>>MODE: Boil</a><br>
<a href=?cmd=6&sid=<?php print $rnd;?>>MODE: Heat</a><br>

<?php
    endif;
    
if ($command == 1):
    //print "command ON<br>\n";
    exec("/usr/bin/python3 /home/pi/Programming/kettle_on.py", $output);
    print($output[0]);
elseif ($command == 2):
    //print "command OFF<br>\n";
    exec("/usr/bin/python3 /home/pi/Programming/kettle_off.py", $output);
    print($output[0]);
elseif ($command == 3):
    print "command TEST<br>\n";
    exec("/usr/bin/python3 /home/pi/Programming/kettle_test.py", $output);
    print_arr ($output);
elseif ($command == 4):
    //print "command JSON<br>\n";
    exec("/usr/bin/python3 /home/pi/Programming/kettle_json.py", $output);
    print($output[0]);
endif;

function print_arr($arr)
{
    foreach ($arr as $line)
    {
        print $line."<br>\n";
    }
}

?>
