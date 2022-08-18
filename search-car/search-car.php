<?php
/**
 * Plugin Name: Expert Search Car
 * Description: Search Car Form
 * Version: 1.0.0
 * Author: Expert2014
 * Author URI: https://fiverr.com/exper2014
 * Text Domain: searchcar
 * Domain Path: /languages
 */

if ( ! defined( 'ABSPATH' ) ) {
  exit; // Exit if accessed directly.
}

// Define Constant
define('SEARCHC_PATH',  plugin_dir_path( __FILE__ ) );

// Load the plugin
add_action( 'plugins_loaded', 'searchc_pluign' );

function searchc_pluign() {
  require_once SEARCHC_PATH . 'aws/aws-autoloader.php';
  require_once SEARCHC_PATH . 'awss3.php';

  // Init actions
  searchc_init_actions();
}

function searchc_enqueue_scripts() {
    
    wp_enqueue_script( 'searchc-plugins', plugins_url( 'js/plugins.js', __FILE__ ), array('jquery'), false, true );
    wp_enqueue_script( 'searchc-nice-select', plugins_url( 'js/jquery.nice-select.js', __FILE__ ), array('jquery'), false, true );
    wp_enqueue_script( 'searchc-scripts', plugins_url( 'js/scripts.js', __FILE__ ), array('jquery'), false, true );
    wp_localize_script( 'searchc-scripts', 'wpAjaxUrl', array( 'ajaxurl' => admin_url( 'admin-ajax.php' )) );
    wp_enqueue_style( 'nice-select-css', plugins_url( 'css/nice-select.css', __FILE__ ) );
    wp_enqueue_style( 'searchc-css', plugins_url( 'css/searchc.css', __FILE__ ) );
}

/*
Shortcode logic how it should be rendered
*/
function render_search_form( $atts, $content = null ) {
	$args = shortcode_atts(
    	['is_homepage' => 'no' ],
    	$atts
    );
    ob_start();
    include 'search-form-view.php';
    $output = ob_get_contents();
    ob_end_clean();
    return $output;
}

/*
Shortcode logic how it should be rendered
*/
function render_search_form_homepage( $atts, $content = null ) {
	
    ob_start();
    include 'search-form-homepage-view.php';
    $output = ob_get_contents();
    ob_end_clean();
    return $output;
}
function render_search_car_as_modal_with_button( $atts, $content = null ) {
	
    ob_start();
    include 'search-car-with-button.php';
    $output = ob_get_contents();
    ob_end_clean();
    return $output;
}

/**
 * Initilize actions
 */
if ( ! function_exists( 'searchc_init_actions' ) ):
  function searchc_init_actions() {
    // Loads frontend scripts and styles
    add_action( 'wp_enqueue_scripts', 'searchc_enqueue_scripts');
    add_shortcode( 'expert_search_form', 'render_search_form' );
  	add_shortcode( 'expert_search_form_homepage', 'render_search_form_homepage' );
  	add_shortcode( 'search_car_as_modal_with_button', 'render_search_car_as_modal_with_button' );
    add_action( 'wp_ajax_fetch-data', 'fetch_data' );
    add_action( 'wp_ajax_nopriv_fetch-data', 'fetch_data' );
  }
endif;
