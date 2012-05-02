<?php
/**
 * To apply and assess, version 3 - filter sets to Google Anaytics data,
 * incorporating support for terms as well as templates, and to exclude numbers.
 * Dauvit King <d.j.king@open.ac.uk> for ViBRANT WP3, January 2012
 */

// to see if Service Provider has a number
function match_number($search_field) {
    if (preg_match('/\d/', $search_field)) {
        return 'numeric value';
    }
    return '';
}

// to see if search terms are found in the Service Provider
// match on token characters, so dsl will match adsl for example
function match_template($search_terms, $search_field) {
    foreach ($search_terms as $token) {
        // have to test this way in case string starts at 0 = false ;-)
        $pos = strpos($search_field, $token);
        if ($pos !== false) {
            return $token;
        }
    }
    return '';
}

// to see if search tokens are found in the Service Provider
// match on exact token only, so dsl will not match adsl for example
function match_term($search_terms, $search_field) {
    foreach ($search_terms as $token) {
        if (preg_match("/\b{$token}\b/", $search_field)) {
            return $token;
        }
    }
    return '';
}

// to calculate precision, recall and f-measure
// overloaded function I know
// should be three separate functions but this is a hack ;-)
function stats($f_pos, $f_neg, $t_pos, $t_neg) {

    // precision [tp/(tp+fp)]
    $divisor = $t_pos + $f_pos;
    if ($divisor != 0) {
        $p = round(($t_pos / $divisor), 2);
    } else {
        $p = 0;
    }

    // recall [tp/(tp+fn)]
    $divisor = $t_pos + $f_neg;
    if ($divisor != 0) {
        $r = round($t_pos / $divisor, 2);
    } else {
        $r = 0;
    }

    // f-measure [(p*r)/(p+r)]
    $divisor = $p + $r;
    if ($divisor != 0) {
        $f = 2 * round(($p * $r) / $divisor, 2);
    } else {
        $f = 0;
    }

    return array($p, $r, $f);
}

// start of script proper
echo "\napply and assess started\n";

// get filter name
if ($argc == 2) {
    $filter = $argv[1];
    echo "using {$filter}\n";
} else {
    exit("\nscript exiting\nno filter file specified\n");
}

// sanity check
if (file_exists($filter . '.php')) {
    require_once($filter . '.php');
} else {
    exit("\nscript exiting\nfilter file {$filter} not found\n");
}

// suppress error messages, such as for accessing empty filter set arrays
ini_set('error_reporting', 'E_ALL & ~E_NOTICE');

// ready the stats
$tot_inc = 0;
$tp_inc = 0;
$fp_inc = 0;
$tn_inc = 0;
$fn_inc = 0;
$tot_exc = 0;
$tp_exc = 0;
$fp_exc = 0;
$tn_exc = 0;
$fn_exc = 0;
$tot_oth = 0;
$tp_oth = 0;
$fp_oth = 0;
$tn_oth = 0;
$fn_oth = 0;

// ready the files
$file_name = 'Clustering/Gold1000B';
// input
$fn_in = $file_name . '.csv';
// $fn_in = 'clustering\Gold1000B.csv';
$fin = fopen($fn_in, 'r') or exit("Unable to open input file {$fn_in}\n");

// marked output
$fn_out = $filename . $fname . '-applied.csv';
$fout = fopen($fn_out, 'w') or exit("Unable to open output file {$fn_out}\n");

// and reports
$fn_include = $file_name . '-' . $filter . '-include.txt';
$finclude= fopen($fn_include, 'w') or exit("Unable to open output file {$fn_include}\n");
$fn_exclude = $file_name . '-' . $filter . '-exclude.txt';
$fexclude = fopen($fn_exclude, 'w') or exit("Unable to open output file {$fn_exclude}\n");
$fn_other = $file_name . '-' . $filter . '-other.txt';
$fother = fopen($fn_other, 'w') or exit("Unable to open output file {$fn_other}\n");

// now classify the input one rowm at a time
while ($row = fgetcsv($fin)) {

    // set defaults 
    $pos = false;
    $row_mark = 'o';

    // test row and apply type according to filter set rules
    $token = match_template($strong_excludes, $row[0]);
    if ($token !== '') {
        $row_mark = 'e';
    } else {
        $token = match_term($strong_excludes_term, $row[0]);
        if ($token !== '') {
            $row_mark = 'e';
        } else {
            $token = match_template($includes, $row[0]);
            if ($token !== '') {
                $row_mark = 'i';
            } else {
                $token = match_term($includes_term, $row[0]);
                if ($token !== '') {
                    $row_mark = 'i';
                } else {
                    $token = match_number($row[0]);
                    if ($token !== '') {
                        $row_mark = 'e';
                    } else {
                        $token = match_template($excludes, $row[0]);
                        if ($token !== '') {
                            $row_mark = 'e';
                        } else {
                            $token = match_term($excludes_term, $row[0]);
                            if ($token !== '') {
                                $row_mark = 'e';
                            }
                        }
                    }
                }
            }
        }
    }

// mark the output

// marking matrix
// i	i	tp_inc	tn_exc	tn_oth
// i	e	fn_inc	fp_exc	tn_oth
// i	o	fn_inc	tn_exc	fp_oth
// e	i	fp_inc	fn_exc	tn_oth
// e	e	tn_inc	tp_exc	tn_oth
// e	o	tn_inc	fn_exc	fp_oth
// o	i	fp_inc	tn_exc	fn_oth
// o	e	tn_inc	fp_exc	fn_oth
// o	o	tn_inc	tn_exc	tp_oth

    $row[] = $row_mark;
    if ($row[3] == 'i') {
        $tot_inc++;
        if ($row_mark == 'i') {
            fwrite($finclude, "found {$token} in {$row[0]}\n");
            $tp_inc++;
            $tn_exc++;
            $tn_oth++;
        } else if ($row_mark == 'e') {
            fwrite($finclude, "found {$token} in {$row[0]} ** marked as exclude **\n");
            $fn_inc++;
            $fp_exc++;
            $tn_oth++;
        } else if ($row_mark == 'o') {
            fwrite($finclude, "nothing found in {$row[0]} ** marked as other **\n");
            $fn_inc++;
            $tn_exc++;
            $fp_oth++;
        }
    } else if ($row[3] =='e') {
        $tot_exc++;
        if ($row_mark == 'i') {
            fwrite($fexclude, "found {$token} in {$row[0]} ** marked as include **\n");
            $fp_inc++;
            $fn_exc++;
            $tn_oth++;
        } else if ($row_mark == 'e') {
            fwrite($fexclude, "found {$token} in {$row[0]}\n");
            $tn_inc++;
            $tp_exc++;
            $tn_oth++;
        }  else if ($row_mark == 'o') {
            fwrite($fexclude, "nothing found in {$row[0]} ** marked as other **\n");
            $tn_inc++;
            $fn_exc++;
            $fp_oth++;
        }
    } else if ($row[3] =='o') {
        $tot_oth++;
        if ($row_mark == 'i') {
            fwrite($fother, "found {$token} in {$row[0]} ** marked as include **\n");
            $fp_inc++;
            $tn_exc++;
            $fn_oth++;
        } else if ($row_mark == 'e') {
            fwrite($fother, "found {$token} in s{$row[0]} ** marked as exclude **\n");
            $tn_inc++;
            $fp_exc++;
            $fn_oth++;
        } else if ($row_mark == 'o') {
            fwrite($fother, "nothing found in {$row[0]}\n");
            $tn_inc++;
            $tn_exc++;
            $tp_oth++;
        }
    }
    // write out marked output
    fputcsv($fout, $row);
}

// prepare the stats
$sum_inc = $tp_inc + $fp_inc + $tn_inc + $fn_inc;
$sum_exc = $tp_exc + $fp_exc + $tn_exc + $fn_exc;
$sum_oth = $tp_oth + $fp_oth + $tn_oth + $fn_oth;

$stats_inc = stats($fp_inc, $fn_inc, $tp_inc, $tn_inc);
$stats_exc = stats($fp_exc, $fn_exc, $tp_exc, $tn_exc);
$stats_oth = stats($fp_oth, $fn_oth, $tp_oth, $tn_oth);

// write out the stats
$line = sprintf("\n\n%-12s %6d\n\n",'includes:', $tot_inc);
fwrite($finclude, $line);
$line = sprintf("%-12s %6d\n", 'false pos:', $fp_inc);
fwrite($finclude, $line);
$line = sprintf("%-12s %6d\n", 'false neg:', $fn_inc);
fwrite($finclude, $line);
$line = sprintf("%-12s %6d\n", 'true pos:', $tp_inc);
fwrite($finclude, $line);
$line = sprintf("%-12s %6d\n", 'true neg:', $tn_inc);
fwrite($finclude, $line);
$line = sprintf("%-12s %6d\n\n", 'sum:', $sum_inc);
fwrite($finclude, $line);
$line = sprintf("%-12s %6.2f\n", 'precision:', $stats_inc[0]);
fwrite($finclude, $line);
$line = sprintf("%-12s %6.2f\n", 'recall:', $stats_inc[1]);
fwrite($finclude, $line);
$line = sprintf("%-12s %6.2f\n", 'f-measure:', $stats_inc[2]);
fwrite($finclude, $line);

$line = sprintf("\n\n%-12s %6d\n\n",'excludes:', $tot_exc);
fwrite($fexclude, $line);
$line = sprintf("%-12s %6d\n", 'false pos:', $fp_exc);
fwrite($fexclude, $line);
$line = sprintf("%-12s %6d\n", 'false neg:', $fn_exc);
fwrite($fexclude, $line);
$line = sprintf("%-12s %6d\n", 'true pos:', $tp_exc);
fwrite($fexclude, $line);
$line = sprintf("%-12s %6d\n", 'true neg:', $tn_exc);
fwrite($fexclude, $line);
$line = sprintf("%-12s %6d\n\n", 'sum:', $sum_exc);
fwrite($fexclude, $line);
$line = sprintf("%-12s %6.2f\n", 'precision:', $stats_exc[0]);
fwrite($fexclude, $line);
$line = sprintf("%-12s %6.2f\n", 'recall:', $stats_exc[1]);
fwrite($fexclude, $line);
$line = sprintf("%-12s %6.2f\n", 'f-measure:', $stats_exc[2]);
fwrite($fexclude, $line);

$line = sprintf("\n\n%-12s %6d\n\n",'other:', $tot_oth);
fwrite($fother, $line);
$line = sprintf("%-12s %6d\n", 'false pos:', $fp_oth);
fwrite($fother, $line);
$line = sprintf("%-12s %6d\n", 'false neg:', $fn_oth);
fwrite($fother, $line);
$line = sprintf("%-12s %6d\n", 'true pos:', $tp_oth);
fwrite($fother, $line);
$line = sprintf("%-12s %6d\n", 'true neg:', $tn_oth);
fwrite($fother, $line);
$line = sprintf("%-12s %6d\n\n", 'sum:', $sum_oth);
fwrite($fother, $line);
$line = sprintf("%-12s %6.2f\n", 'precision:', $stats_oth[0]);
fwrite($fother, $line);
$line = sprintf("%-12s %6.2f\n", 'recall:', $stats_oth[1]);
fwrite($fother, $line);
$line = sprintf("%-12s %6.2f\n", 'f-measure:', $stats_oth[2]);
fwrite($fother, $line);

echo "\n              include  exclude    other\n";
$line = sprintf("%-12s %8d %8d %8d\n", 'totals:', $tot_inc, $tot_exc, $tot_oth);
echo $line;
$line = sprintf("%-12s %8d %8d %8d\n", 'false pos:', $fp_inc, $fp_exc, $fp_oth);
echo $line;
$line = sprintf("%-12s %8d %8d %8d\n", 'false neg:', $fn_inc, $fn_exc, $fn_oth);
echo $line;
$line = sprintf("%-12s %8d %8d %8d\n", 'true pos:', $tp_inc, $tp_exc, $tp_oth);
echo $line;
$line = sprintf("%-12s %8d %8d %8d\n", 'true neg:', $tn_inc, $tn_exc, $tn_oth);
echo $line;
$line = sprintf("%-12s %8d %8d %8d\n\n", 'sum:', $sum_inc, $sum_exc, $sum_oth);
echo $line;
$line = sprintf("%-12s %8.2f %8.2f %8.2f\n", 'precision:', $stats_inc[0], $stats_exc[0], $stats_oth[0]);
echo $line;
$line = sprintf("%-12s %8.2f %8.2f %8.2f\n", 'recall:', $stats_inc[1], $stats_exc[1], $stats_oth[1]);
echo $line;
$line = sprintf("%-12s %8.2f %8.2f %8.2f\n", 'f-measure:', $stats_inc[2], $stats_exc[2], $stats_oth[2]);
echo $line;

// close down the script
fclose($fin) or exit("Unable to close input file {$fn_in}\n");
fclose($fout) or exit("Unable to close output file {$fn_out}\n");
fclose($finclude) or exit("Unable to close output file {$fn_include}\n");
fclose($fexclude) or exit("Unable to close output file {$fn_exclude}\n");
fclose($fother) or exit("Unable to close output file {$fn_other}\n");

echo "\napply and assess finished\n";
?>
