<?
//echo <<<END
//{"days":[{"long":"-111.850766","lat":"40.391617","chance":43,"date":"2013-11-01","event":"leaves budding","zip_code":"84043"},{"long":"-111.850766","lat":"40.391617","chance":52,"date":"2013-11-02","event":"leaves budding","zip_code":"84043"},{"long":"-111.850766","lat":"40.391617","chance":67,"date":"2013-11-03","event":"leaves budding","zip_code":"84043"},{"long":"-111.850766","lat":"40.391617","chance":73,"date":"2013-11-04","event":"leaves budding","zip_code":"84043"},{"long":"-111.850766","lat":"40.391617","chance":85,"date":"2013-11-05","event":"leaves budding","zip_code":"84043"},{"long":"-111.850766","lat":"40.391617","chance":93,"date":"2013-11-06","event":"leaves budding","zip_code":"84043"},{"long":"-111.850766","lat":"40.391617","chance":95,"date":"2013-11-07","event":"leaves budding","zip_code":"84043"},{"long":"-111.850766","lat":"40.391617","chance":86,"date":"2013-11-08","event":"leaves budding","zip_code":"84043"},{"long":"-111.850766","lat":"40.391617","chance":72,"date":"2013-11-09","event":"leaves budding","zip_code":"84043"},{"long":"-111.850766","lat":"40.391617","chance":61,"date":"2013-11-10","event":"leaves budding","zip_code":"84043"}]}
//END;
//exit;


$var = json_decode($_REQUEST['data'], true);
$var = json_encode($var);

$var = escapeshellarg($var);
$result_raw = shell_exec("/home2/jonnymoo/anaconda/bin/python pheno2.py $var 2>&1");
$result = json_decode($result_raw, true);
if($result === null){
	echo "Error or Debug: " . $result_raw;
	exit;
}

echo json_encode($result);