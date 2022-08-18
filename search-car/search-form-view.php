<div class="header-custom-input" id="header-custom-input">
<!-- 	<div class="choose-menu-custom">
        <input checked="checked" id="buy-car" type="radio" name="choose-buy-sell" value="buy-car" />
        <label class="choose-car-btn buy-car" for="buy-car" id="label-buy-car" style="margin-left: -7px;">Buy a car</label>
        <input id="sell-car" type="radio" name="choose-buy-sell" value="sell-car" />
        <label class="choose-car-btn sell-car" for="sell-car" id="label-sell-car" >Sell a car</label>
    </div> -->
	<div class="c-col-1">
		<input id="carsearch1" class="custom-input" type="text" placeholder="Enter a Make or Model">
    	<div class="spinner spinner-slow" id="carsearch1loading" style="display: none;"></div>
<!--     	<img src="https://autogenie.co.uk/wp-content/uploads/2022/02/search-icon.svg" class="search-icon-field hide-mobile" id="car-search-btn-svg"> -->
        <div class="dropdown-menu-custom">
        	<select id="carsearch1-select" style="display: none;">
        		<option>Buy</option>
            	<option>Sell</option>
        	</select><div class="nice-select" tabindex="0"><span class="current">Buy</span><ul class="list"><li data-value="Buy" class="option selected">Buy</li><li data-value="Sell" class="option">Sell</li></ul></div>
    	</div>
	</div>
	<button class="search-btn" id="car-search-btn">Choose</button>
</div>
<div id="newsletter" class="form-wrap" style="display: none;">
	<form id="mc-embedded-subscribe-form" name="mc-embedded-subscribe-form" class="validate" novalidate="novalidate">
		<div class="flex-wrapper">
			<div class="form-field">
				<input type="text" name="newsletter_email" id="newsletter_email" value="" placeholder="Enter your email address" class="custom-input" required>
			</div>
			<div class="form-submit">
				<input type="submit" name="newsletter_submit" id="newsletter_submit" value="Subscribe" class="search-btn">
			</div>
		</div>
	</form>
	<div class="loading" style="display: none;">
		<span class="bounce1"></span>
		<span class="bounce2"></span>
		<span class="bounce3"></span>
	</div>
	<div class="success" style="display: none;"></div>
</div>
<!-- <div class="spinner spinner-slow" id="carsearch1loading" style="display: block; position: absolute; top: 419.07px; left: 965px;"></div> -->