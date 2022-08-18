<?php
if ( ! defined( 'ABSPATH' ) ) {
  exit; // Exit if accessed directly.
}

use Aws\S3\S3Client;  
use Aws\Credentials\Credentials;
use Aws\Exception\AwsException;

function fetch_data() {
    
    $credentials = new Credentials("D4BC0406K2VIJFXZ4I58", "0DniJ5DjPRACHQvdpTkPYeRXkc3SMknMiD5ebiNT");

    $bucket = "autogenieaws";
    $objectKey = "data.json";

    //Instantiate the S3 client with your AWS credentials
    $s3Client = new S3Client([
        'version' => 'latest',
        'region'  => 'us-east-1',
        'endpoint' => 'https://ewr1.vultrobjects.com/',
        'credentials' => [
            'key'    => 'D4BC0406K2VIJFXZ4I58',
            'secret' => '0DniJ5DjPRACHQvdpTkPYeRXkc3SMknMiD5ebiNT'
        ],
    ]);

    // try {
    //     $s3Client = new S3Client([
    //         'version' => 'latest',
    //         'region'  => 'us-east-1',
    //         'endpoint' => 'https://ewr1.vultrobjects.com/',
    //         'credentials' => [
    //             'key'    => 'D4BC0406K2VIJFXZ4I58',
    //             'secret' => '0DniJ5DjPRACHQvdpTkPYeRXkc3SMknMiD5ebiNT'
    //         ],
    //     ]);
    // } catch (Aws\S3\Exception\S3Exception $e) {
    //     wp_send_json_error($e->getAwsErrorMessage());
    // }
    $params = array(
        'Bucket' => $bucket,
        'Key' => $objectKey,
        'ResponseContentType' => 'json'
    );
    try {
        
        $result = $s3Client->getObject($params);
    	ob_clean();
		echo $result['Body']->getContents();
		exit();

    } catch (Aws\S3\Exception\S3Exception $e) {
    	ob_clean();
        echo $e->getAwsErrorMessage();
    	exit();
    }

	// $reuslt = array('brands' => array(
	// 'brand' => array(
	// 'name' => 'Audi',
	// 'title' => 'Audi',
	// 'model' => '2022'
	// )
	// ));

    
}
