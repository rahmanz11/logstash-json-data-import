function fkhShowSubscriptionForm ()
{

	document.getElementById("header-custom-input").style.display = "none";
	document.getElementById("newsletter").style.display = "block";

	
	//document.getElementById("subscription_mobile").style.display = "block";

	document.getElementById("buying_selling_desktop").style.display = "none";
	document.getElementById("buying_selling_mobile").style.display = "none";

	if (document.getElementById("carsearch1-select").value === "Buy")
    {
    	document.getElementById("subscription_buy_desktop").style.display = "block";
    	document.getElementById("buyMessage").style.display = "block";
    }
	else
    {
    	document.getElementById("subscription_sell_desktop").style.display = "block";
    	document.getElementById("sellMessage").style.display = "block";
    }
}

(function ($) {
    $(window).on('load', function () {
        $('.fade-in').css({ position: 'relative', opacity: 0, top: -14 });
        setTimeout(function () {
            $('#preload-content').fadeOut(400, function () {
                $('#preload').fadeOut(800);
                setTimeout(function () {
                    $('.fade-in').each(function (index) {
                        $(this)
                            .delay(400 * index)
                            .animate({ top: 0, opacity: 1 }, 800);
                    });
                }, 800);
            });
        }, 400);
    });

    $(document).ready(function () {

        $('select').niceSelect();
    
    	$(".dropdown-menu-custom").on('change', 'select', function() {
  			var buyorsell = $("#carsearch1-select").val();
  			if( buyorsell == 'Buy' ){
            	$('#car-search-btn').text('Choose');
            }else {
            	$('#car-search-btn').text('Search');
            }
		});

        if ($("input[name=choose-buy-sell]:checked")) {

            $id = $('input[name=choose-buy-sell]:checked').attr('id');
            $('#label-' + $id).addClass('label-background');
        }

        $('#searchModal').on('show.bs.modal', function () {
            if ($("input[name=choose-buy-sell]:checked")) {

                $id = $('input[name=choose-buy-sell]:checked').attr('id');
                $('#label-' + $id).addClass('label-background');
            }

            $('#carsearch1').on('change', function (e) {
                console.log(e.target.value);
            });

        });

        $('#carsearch-homepage').on('click focus', function (e) {

            e.preventDefault();
            $('#searchModal').modal('show');

        });

        $('#carsearch-footer').on('click focus', function (e) {

            e.preventDefault();
            $('#searchModal').modal('show');

        });

        $("input[name=choose-buy-sell]").change(function () {

            if ($(this).is(":checked")) {
                $id = $(this).attr('id');

                if ($id == 'buy-car') {
                    $('#label-sell-car').removeClass('label-background');
                    $('#label-buy-car').addClass('label-background');

                } else {
                    $('#label-buy-car').removeClass('label-background');
                    $('#label-sell-car').addClass('label-background');

                }


            }
        });
    
    	//debugger;
        // Create a countdown instance. Change the launchDay according to your needs.
        // The month ranges from 0 to 11. I specify the month from 1 to 12 and manually subtract the 1.
        // Thus the launchDay below denotes 7 May, 2014.
        var launchDay = new Date(2018, 1 - 1, 18);
        $('#timer').countdown({
            until: launchDay,
        });

        // Add background slideshow
 //       $.backstretch(['images/bg1.jpg'], {
  //          fade: 750,
  //          duration: 4000,
   //     });

        // Invoke the Placeholder plugin
        $('input, textarea').placeholder();

        // Validate newsletter form
        $('<div class="loading"><span class="bounce1"></span><span class="bounce2"></span><span class="bounce3"></span></div>').hide().appendTo('.form-wrap');
        $('<div class="success"></div>').hide().appendTo('.form-wrap');

        // Open modal window on click
        $('#modal-open').on('click', function (e) {
            var mainInner = $('#main .inner'),
                modal = $('#modal');

            mainInner.animate({ opacity: 0 }, 400, function () {
                $('html,body').scrollTop(0);
                modal.addClass('modal-active').fadeIn(400);
            });
            e.preventDefault();

            $('#modal-close').on('click', function (e) {
                modal.removeClass('modal-active').fadeOut(400, function () {
                    mainInner.animate({ opacity: 1 }, 400);
                });
                e.preventDefault();
            });
        });

        console.log('hit');
        //$=jQuery;
        displaytimer = null;
        releasetimer = null;
        displayopen = false;
        //inputfield = "carsearch";
        //setTimeout(function(){
        // $(".autocomplete-items").css("height",($(window).height()*.25)+"px");
        // $(".autocomplete-items").css("width",($("#"+inputfield).width()+20)+"px");
        //},200)
        showdetailsinblankpage = false;
        selval = null;
        focussed = null;
        isselected = false;

        function autocompleted(inpt, inputfield, adjust) {
            inp = inpt;
            /*the autocomplete function takes two arguments,
  the text field element and an array of possible autocompleted values:*/
            var currentFocus;
            /*execute a function when someone writes in the text field:*/
            $('body').append('<div class = "spinner spinner-slow" id = "' + inputfield + 'loading' + '"></img>');
            $('#' + inputfield + 'loading').css('display', 'none');
            $('#' + inputfield + 'loading').css('top', '22.5px');
            $('#' + inputfield + 'loading').css('right', '82px');
            // https://cdnjs.cloudflare.com/ajax/libs/fancybox/2.1.5/fancybox_loading.gif
            //  $("#"+inputfield+"loading").attr("src","https://i.giphy.com/media/jAYUbVXgESSti/giphy.webp");
            //  $("#"+inputfield+"loading").css("margin","auto");
            //  $("#"+inputfield+"loading").css("width","24px");
            //  $("#"+inputfield+"loading").css("height","24px");
            //  $("#"+inputfield+"loading").css("background-color","rgb(255, 255, 255)");
            //  $("#"+inputfield+"loading").css("transition","background-color 300ms");
            $('#' + inputfield + 'loading').css('position', 'absolute');
            inp.addEventListener('click', function (e) {
                e.stopPropagation();
                e.preventDefault();
                focussed = e.srcElement.id;
                tval = $('#' + focussed).val();
                tid = focussed;
                tobj = $('#' + focussed);
                if (releasetimer) {
                    clearTimeout(releasetimer);
                }
                releasetimer = setTimeout(function () {
                    autocompletelist(tval, tid, tobj);
                }, 1000);
            });
            $('#' + inputfield + ' #' + inputfield + 'autocomplete-list')
                .focus(function (e) {
                    e.stopPropagation();
                    e.preventDefault();
                    $('#' + inputfield + 'autocomplete-list').each(function () {
                        $(this).show();
                    });
                })
                .blur(function (e) {
                    e.stopPropagation();
                    e.preventDefault();
                    $('#' + inputfield + 'autocomplete-list').each(function () {
                        $(this).hide();
                    });
                });
            inp.addEventListener('focus', function (e) {
                focussed = e.srcElement.id;
            });
            if ($('#' + focussed).val()) {
                tobj = $('#' + focussed);
                tval = $('#' + focussed).val();
                tid = focussed;
                $('#' + inputfield + 'loading').css('display', 'block');
                if (releasetimer) {
                    clearTimeout(releasetimer);
                }
                releasetimer = setTimeout(function () {
                    autocompletelist(tval, tid, tobj);
                }, 1000);
            }
            inp.addEventListener('input', function (e) {
                if (displaytimer) {
                    displayopen = false;
                    clearInterval(displaytimer);
                }
                e.stopPropagation();
                e.preventDefault();
                tval = $('#' + focussed).val();
                tid = focussed;
                tobj = $('#' + focussed);
                if (releasetimer) {
                    clearTimeout(releasetimer);
                }
                releasetimer = setTimeout(function () {
                    autocompletelist(tval, tid, tobj);
                }, 500);
            });
            /*execute a function presses a key on the keyboard:*/
            inp.addEventListener('keydown', function (e) {
                focussed = e.srcElement.id;
                $('#' + focussed + 'loading').css('display', 'block');
                var x = document.getElementById(this.id + 'autocomplete-list');
                if (x) x = x.getElementsByTagName('div');
                if (e.keyCode == 40) {
                    /*If the arrow DOWN key is pressed,
        increase the currentFocus variable:*/
                    currentFocus++;
                    /*and and make the current item more visible:*/
                    addActive(x);
                } else if (e.keyCode == 38) {
                    //up
                    /*If the arrow UP key is pressed,
        decrease the currentFocus variable:*/
                    currentFocus--;
                    /*and and make the current item more visible:*/
                    addActive(x);
                } else if (e.keyCode == 13) {
                    /*If the ENTER key is pressed, prevent the form from being submitted,*/
                    e.preventDefault();
                    if (currentFocus > -1) {
                        /*and simulate a click on the "active" item:*/
                        if (x) x[currentFocus].click();
                    }
                }
            });
        }
        function addActive(x) {
            /*a function to classify an item as "active":*/
            if (!x) return false;
            /*start by removing the "active" class on all items:*/
            removeActive(x);
            if (currentFocus >= x.length) currentFocus = 0;
            if (currentFocus < 0) currentFocus = x.length - 1;
            /*add class "autocomplete-active":*/
            x[currentFocus].classList.add('autocomplete-active');
        }
        function removeActive(x) {
            /*a function to remove the "active" class from all autocomplete items:*/
            for (var i = 0; i < x.length; i++) {
                x[i].classList.remove('autocomplete-active');
            }
        }
        function closeAllLists(elmnt) {
            /*close all autocomplete lists in the document,
    except the one passed as an argument:*/
            var x = document.getElementById(elmnt + 'autocomplete-list');
            if (x) {
                x.parentNode.removeChild(x);
                //        for (var i = 0; i < x.length; i++){
                //             x[i].parentNode.removeChild(x[i]);
                //        }
            }
        }

        var a, b, i, val;
        function autocompletelist(eeval, eid, eobj) {
            if (displaytimer) {
                displayopen = false;
                clearInterval(displaytimer);
            }
            a, b, i, (val = eeval);
            var autocompletevalue = $('#' + focussed).val();
            closeAllLists(focussed);
            if (!autocompletevalue) {
                $('#' + focussed + 'loading').css('display', 'none');
                return false;
            }
            currentFocus = -1;
            elem = document.createElement('div');
            elem.setAttribute('id', eid + 'autocomplete-list');
            elem.setAttribute('class', 'autocomplete-items');
            elem.setAttribute('rel', focussed);
            /*append the DIV element as a child of the autocomplete container:*/
            $('.header-custom-input .c-col-1').append("<div id='act'></div>");
            //	 $(eobj).parent().parent().parent().parent().append("<div id = 'act'></div>")
            $('#act').attr('class', '').show();
            $('body').on('click', function () {
                $('#act').hide();
            });
            $('#act').append(elem);
            //   setTimeout(function(){
            //   https://cdnjs.cloudflare.com/ajax/libs/fancybox/2.1.5/fancybox_loading.gif
            $('[rel="' + focussed + '"]').css('height', '380px');
            //  $('[rel="'+focussed+'"]').css("width",("100%");
            //     $(".autocomplete-items").css("margin-left",$("#"+focussed).offset().left-88.5)+"px");
            //  $('[rel="'+focussed+'"]').css("left",($("#"+focussed).offset().left-50)+"px");
            //  $('[rel="'+focussed+'"]').css("top",($("#"+focussed).offset().top+60)+"px");

            //     $(".autocomplete-items").css("margin-top","15px");
            //   },200)
            //   dtselected = eval("x_"+autocompletevalue.toUpperCase().substr(0,1));

            dtselected = finaldata;
            dtsselected = [];
            yrsselected = [];
            yearsearch = [];
            var autoval = autocompletevalue;
            for (ikey in dtselected) {
                yearslist = [];
                for (iyear = 0; iyear < dtselected[ikey].length; iyear++) {
                    if (dtselected[ikey][iyear].yearstart) {
                        yearslist.push(parseInt(dtselected[ikey][iyear].yearstart));
                    }
                    if (dtselected[ikey][iyear].yearstop) {
                        yearslist.push(parseInt(dtselected[ikey][iyear].yearstop));
                    }
                }
                yearslist = yearslist.sort(function (a, b) {
                    if (a < b) {
                        return -1;
                    }
                    if (a > b) {
                        return 1;
                    }
                    return 0;
                });
                yrstart = yearslist[0];
                yrend = yearslist[yearslist.length - 1];
                years = '';
                for (iyr = yrstart; iyr < yrend + 1; iyr++) {
                    years += ', ' + iyr;
                }
                yrchk = years;
                years = years.substr(2);
                ikeys = ikey.split(' ').join('  ');
                ixkeys = ikeys;
                izkeys = ikeys;
                izzkeys = ikeys;
                izkeys = izkeys.replace(/[^a-z\d\s]+/gi, '');
                izzkeys = izzkeys.replace(/[^a-z\d\s]+/gi, ' ');
                ixkeys = ixkeys.replace(/[^a-zA-Z0-9]/g, '');
                var autocompletevalue1 = autoval.replace(/[^a-z\d\s]+/gi, ' ');
                autocompletevalue = autocompletevalue.replace(/[^a-zA-Z0-9]/g, '');
                isbacknumber = '';
                numb = '0,1,2,3,4,5,6,7,8,9,';
                fnumb = '';
                for (iykeys = ixkeys.length; iykeys >= 0; iykeys--) {
                    if (numb.indexOf(ixkeys.substr(iykeys, 1) + ',')) {
                        fnumb += ixkeys.substr(iykeys, 1);
                    } else {
                        fnumb = '';
                        break;
                    }
                    ffnumb = '';
                    if (fnumb) {
                        ffnumb = ikey.split(fnumb);
                        ffnumb = ffnumb[0];
                    }
                }
                if (
                    izkeys.toUpperCase().indexOf(autocompletevalue.toUpperCase()) < 0 &&
                    izzkeys.toUpperCase().indexOf(autocompletevalue.toUpperCase()) < 0 &&
                    ixkeys.toUpperCase().indexOf(autocompletevalue.toUpperCase()) < 0
                ) {
                    if (ffnumb && ikeys.toUpperCase().indexOf(ffnumb.toUpperCase()) > -1) {
                        if (yrchk.indexOf(', ' + fnumb) > -1) {
                            yr = {};
                            yr.name = ikey;
                            yr.years = years;
                            if (yrchk.indexOf(', ' + autocompletevalue) > -1 || yrchk == ', ' + autocompletevalue) {
                                y = {};
                                y.name = ikey;
                                y.status = true;
                                yearsearch.push(y);
                            } else {
                                y = {};
                                y.name = ikey;
                                y.status = false;
                                yearsearch.push(y);
                            }
                            yrsselected.push(yr);
                            ikeyx = {};
                            ikeyx.name = ikey;
                            ikeyx.option = -1;
                        }
                        check1 = izzkeys.split(' ');
                        check2 = autocompletevalue1.split(' ');
                        include = false;
                        founds = 0;
                        for (icheck2 = 0; icheck2 < check2.length; icheck2++) {
                            if (check2[icheck2].trim().length === 0) {
                                continue;
                            }
                            for (icheck1 = 0; icheck1 < check1.length; icheck1++) {
                                if (check1[icheck1].trim().length === 0) {
                                    continue;
                                }
                                if (check1[icheck1].trim().toUpperCase() === check2[icheck2].trim().toUpperCase()) {
                                    founds++;
                                    break;
                                }
                            }
                            if (founds === check2.length) {
                                include = true;
                                break;
                            }
                        }
                        if (include) {
                            yr = {};
                            yr.name = ikey;
                            yr.years = years;
                            if (yrchk.indexOf(', ' + autocompletevalue) > -1 || yrchk == ', ' + autocompletevalue) {
                                y = {};
                                y.name = ikey;
                                y.status = true;
                                yearsearch.push(y);
                            } else {
                                y = {};
                                y.name = ikey;
                                y.status = false;
                                yearsearch.push(y);
                            }
                            yrsselected.push(yr);
                            ikeyx = {};
                            ikeyx.name = ikey;
                            ikeyx.option = 4;
                            dtsselected.push(ikeyx);
                            datafound = true;
                        }
                        continue;
                    }
                }
                if (izkeys.toUpperCase().indexOf(autocompletevalue.toUpperCase()) > -1) {
                    ikeyx = {};
                    ikeyx.name = ikey;
                    ikeyx.option = 1;
                    dtsselected.push(ikeyx);
                    yr = {};
                    yr.name = ikey;
                    yr.years = years;
                    if (yrchk.indexOf(', ' + autocompletevalue) > -1 || yrchk == ', ' + autocompletevalue) {
                        y = {};
                        y.name = ikey;
                        y.status = false;
                        yearsearch.push(y);
                    } else {
                        y = {};
                        y.name = ikey;
                        y.status = false;
                        yearsearch.push(y);
                    }
                    yrsselected.push(yr);
                    continue;
                }
                if (izzkeys.toUpperCase().indexOf(autocompletevalue.toUpperCase()) > -1) {
                    ikeyx = {};
                    ikeyx.name = ikey;
                    ikeyx.option = 2;
                    dtsselected.push(ikeyx);
                    yr = {};
                    yr.name = ikey;
                    yr.years = years;
                    if (yrchk.indexOf(', ' + autocompletevalue) > -1 || yrchk == ', ' + autocompletevalue) {
                        y = {};
                        y.name = ikey;
                        y.status = false;
                        yearsearch.push(y);
                    } else {
                        y = {};
                        y.name = ikey;
                        y.status = false;
                        yearsearch.push(y);
                    }
                    yrsselected.push(yr);
                    continue;
                }

                if (ixkeys.toUpperCase().indexOf(autocompletevalue.toUpperCase()) > -1 && izzkeys.toUpperCase().indexOf(autocompletevalue1.toUpperCase()) > -1) {
                    ikeyx = {};
                    ikeyx.name = ikey;
                    ikeyx.option = 3;
                    dtsselected.push(ikeyx);
                    yr = {};
                    yr.name = ikey;
                    yr.years = years;
                    if (yrchk.indexOf(', ' + autocompletevalue) > -1 || yrchk == ', ' + autocompletevalue) {
                        y = {};
                        y.name = ikey;
                        y.status = false;
                        yearsearch.push(y);
                    } else {
                        y = {};
                        y.name = ikey;
                        y.status = false;
                        yearsearch.push(y);
                    }
                    yrsselected.push(yr);
                    continue;
                }

                if (izzkeys.toUpperCase().indexOf(autocompletevalue1.toUpperCase()) > -1) {
                    ikeyx = {};
                    ikeyx.name = ikey;
                    ikeyx.option = 3;
                    dtsselected.push(ikeyx);
                    yr = {};
                    yr.name = ikey;
                    yr.years = years;
                    if (yrchk.indexOf(', ' + autocompletevalue) > -1 || yrchk == ', ' + autocompletevalue) {
                        y = {};
                        y.name = ikey;
                        y.status = false;
                        yearsearch.push(y);
                    } else {
                        y = {};
                        y.name = ikey;
                        y.status = false;
                        yearsearch.push(y);
                    }
                    yrsselected.push(yr);
                    continue;
                }

                if (ikeys.toUpperCase().indexOf(autocompletevalue.toUpperCase()) > -1 || yrchk.indexOf(', ' + autocompletevalue) > -1) {
                    yr = {};
                    yr.name = ikey;
                    yr.years = years;
                    if (yrchk.indexOf(', ' + autocompletevalue) > -1 || yrchk == ', ' + autocompletevalue) {
                        y = {};
                        y.name = ikey;
                        y.status = true;
                        yearsearch.push(y);
                    } else {
                        y = {};
                        y.name = ikey;
                        y.status = false;
                        yearsearch.push(y);
                    }
                    yrsselected.push(yr);
                    ikeyx = {};
                    ikeyx.name = ikey;
                    ikeyx.option = 4;
                    dtsselected.push(ikeyx);
                    datafound = true;
                }
                check1 = izzkeys.split(' ');
                check2 = autocompletevalue1.split(' ');
                include = false;
                founds = 0;
                yrfound = false;
                for (icheck2 = 0; icheck2 < check2.length; icheck2++) {
                    if (check2[icheck2].trim().length === 0) {
                        continue;
                    }
                    for (icheck1 = 0; icheck1 < check1.length; icheck1++) {
                        if (check1[icheck1].trim().length === 0) {
                            continue;
                        }
                        if (check1[icheck1].trim().toUpperCase() === check2[icheck2].trim().toUpperCase()) {
                            founds++;
                            break;
                        }
                        if (yrchk.indexOf(', ' + check2[icheck2].trim()) > -1) {
                            yrfound = true;
                            founds++;
                            break;
                        }
                    }
                    if (founds === check2.length) {
                        include = true;
                        break;
                    }
                }
                if (include) {
                    yr = {};
                    yr.name = ikey;
                    yr.years = years;
                    if (yrfound) {
                        y = {};
                        y.name = ikey;
                        y.yrstatus = true;
                        y.status = false;
                        yearsearch.push(y);
                    } else {
                        y = {};
                        y.name = ikey;
                        y.status = false;
                        yearsearch.push(y);
                    }
                    yrsselected.push(yr);
                    ikeyx = {};
                    ikeyx.name = ikey;
                    ikeyx.option = 3;
                    dtsselected.push(ikeyx);
                    datafound = true;
                    continue;
                }
                check1 = izzkeys.split(' ').join('');
                check2 = autocompletevalue1.split(' ');
                include = false;
                founds = 0;
                yrfound = false;
                for (icheck2 = 0; icheck2 < check2.length; icheck2++) {
                    if (check2[icheck2].trim().length === 0) {
                        continue;
                    }
                    if (check1.trim().toUpperCase().indexOf(check2[icheck2].trim().toUpperCase()) > -1) {
                        founds++;
                        continue;
                    }
                    if (yrchk.indexOf(', ' + check2[icheck2].trim()) > -1) {
                        yrfound = true;
                        founds++;
                    }
                    if (founds === check2.length) {
                        include = true;
                        break;
                    }
                }
                if (include) {
                    yr = {};
                    yr.name = ikey;
                    yr.years = years;
                    if (yrfound) {
                        y = {};
                        y.name = ikey;
                        y.yrstatus = true;
                        y.status = false;
                        yearsearch.push(y);
                    } else {
                        y = {};
                        y.name = ikey;
                        y.status = false;
                        yearsearch.push(y);
                    }
                    yrsselected.push(yr);
                    ikeyx = {};
                    ikeyx.name = ikey;
                    ikeyx.option = 3;
                    dtsselected.push(ikeyx);
                    datafound = true;
                    continue;
                }
            }
        
            dtsselected.sort(function (a, b) {
                var nameA = a.name.toLowerCase(),
                    nameB = b.name.toLowerCase();
                if (nameA < nameB)
                    //sort string ascending
                    return -1;
                if (nameA > nameB) return 1;
                return 0; //default return value (no sorting)
            });
            yrsselected.sort(function (a, b) {
                var nameA = a.name.toLowerCase(),
                    nameB = b.name.toLowerCase();
                if (nameA < nameB)
                    //sort string ascending
                    return -1;
                if (nameA > nameB) return 1;
                return 0; //default return value (no sorting)
            });
            yearsearch.sort(function (a, b) {
                var nameA = a.name.toLowerCase(),
                    nameB = b.name.toLowerCase();
                if (nameA < nameB)
                    //sort string ascending
                    return -1;
                if (nameA > nameB) return 1;
                return 0; //default return value (no sorting)
            });
            displaytimer = null;
            displaycount = -1;
            displayopen = true;
            if (dtsselected.length == 0) {
                b = document.createElement('div');
                b.style.zIndex = '10000000';
                b.innerHTML = 'No car data available';
                b.style.fontSize = '20px';
                b.style.backgroundColor = 'white';
                b.style.fontWeight = 'bolder';
                b.style.paddingTop = '20%';
                b.style.position = 'absolute';
                b.style.textAlign = 'center';
                b.style.height = '100%';
                b.style.width = '100%';
                elem.appendChild(b);
            }
            var yrpos = -1;
            var yrlength = -1;
            displaytimer = setInterval(function () {
                if (displayopen) {
                    displaycount++;
                    if (displaycount > dtsselected.length - 1) {
                        $('#' + eid + 'loading').css('display', 'none');
                        clearInterval(displaytimer);
                        return;
                    }
                    $('#' + eid + 'loading').css('display', 'none');
                    displayopen = false;
                    b = document.createElement('div');
                    b.style.zIndex = '10000000';
                    b.setAttribute('id', eid + '_' + displaycount);
                    xdetails = dtsselected[displaycount].name.split(' ').join(' ');
                    xlength = autocompletevalue.length;
                    if (!yearsearch[displaycount].status) {
                        xpos = xdetails.toUpperCase().indexOf(autocompletevalue.toUpperCase());
                        if (xpos == -1) {
                        	
                            datastatus = [];
                            xdata1 = xdetails.split(' ');
                            for (ixdata1 = 0; ixdata1 < xdata1.length; ixdata1++) {
                                d = {};
                                d.name = xdata1[ixdata1];
                                if (dtsselected[displaycount].option == 1) {
                                    d.cname = xdata1[ixdata1].replace(/[^a-z\d\s]+/gi, '');
                                    d.option = 1;
                                    d.updated = false;
                                }
                                if (dtsselected[displaycount].option == 2) {
                                    d.cname = xdata1[ixdata1].replace(/[^a-z\d\s]+/gi, ' ');
                                    d.option = 2;
                                    d.updated = false;
                                }
                                if (dtsselected[displaycount].option == 3) {
                                    d.cname = xdata1[ixdata1].replace(/[^a-zA-Z0-9]/g, '');
                                    d.option = 3;
                                    d.updated = false;
                                }
                                if (dtsselected[displaycount].option == 4) {
                                    d.cname = xdata1[ixdata1];
                                    d.option = 4;
                                    d.updated = false;
                                }
                                datastatus.push(d);
                                
                            }
                            xdata2 = autocompletevalue;
                            foundmatch = false;
                            if (dtsselected[displaycount].option == 1) {
                                xreschar = '';
                                for (ichar = 0; ichar < xdata2.length; ichar++) {
                                    xreschar += xdata2.substr(ichar, 1);
                                    for (idata = 0; idata < datastatus.length; idata++) {
                                        if (!datastatus[idata].updated) {
                                            foundstring = false;
                                            for (idata1 = idata - 1; idata1 >= 0; idata1--) {
                                                if (!datastatus[idata].updated && datastatus[idata1].cname.toUpperCase().indexOf(xreschar.toUpperCase()) > -1) {
                                                    foundstring = true;
                                                    break;
                                                }
                                            }
                                            if (foundstring && idata1 < idata) {
                                                continue;
                                            }
                                            xreschar = '';
                                            datastatus[idata].updated = true;
                                            foundmatch = true;
                                        }
                                    }
                                }
                            }
                            if (dtsselected[displaycount].option == 2) {
                                xreschar = '';
                                for (ichar = 0; ichar < xdata2.length; ichar++) {
                                    xreschar += xdata2.substr(ichar, 1);
                                    for (idata = 0; idata < datastatus.length; idata++) {
                                        if (!datastatus[idata].updated) {
                                            foundstring = false;
                                            for (idata1 = idata - 1; idata1 >= 0; idata1--) {
                                                if (!datastatus[idata].updated && datastatus[idata1].cname.toUpperCase().indexOf(xreschar.toUpperCase()) > -1) {
                                                    foundstring = true;
                                                    break;
                                                }
                                            }
                                            if (foundstring && idata1 < idata) {
                                                continue;
                                            }
                                            xreschar = '';
                                            datastatus[idata].updated = true;
                                            foundmatch = true;
                                        }
                                    }
                                }
                            }
                            if (dtsselected[displaycount].option == 3) {
                                xreschar = '';
                                for (ichar = 0; ichar < xdata2.length; ichar++) {
                                    xreschar += xdata2.substr(ichar, 1);
                                    for (idata = 0; idata < datastatus.length; idata++) {
                                        if (!datastatus[idata].updated) {
                                            foundstring = false;
                                            for (idata1 = idata - 1; idata1 >= 0; idata1--) {
                                                if (!datastatus[idata].updated && datastatus[idata1].cname.toUpperCase().indexOf(xreschar.toUpperCase()) > -1) {
                                                    foundstring = true;
                                                    break;
                                                }
                                            }
                                            if (foundstring && idata1 < idata) {
                                                continue;
                                            }
                                            xreschar = '';
                                            datastatus[idata].updated = true;
                                            foundmatch = true;
                                        }
                                    }
                                }
                            }
                            if (dtsselected[displaycount].option == 4) {
                                xreschar = '';
                                for (ichar = 0; ichar < xdata2.length; ichar++) {
                                    xreschar += xdata2.substr(ichar, 1);
                                    for (idata = 0; idata < datastatus.length; idata++) {
                                        if (!datastatus[idata].updated) {
                                            foundstring = false;
                                            for (idata1 = idata - 1; idata1 >= 0; idata1--) {
                                                if (!datastatus[idata].updated && datastatus[idata1].cname.toUpperCase().indexOf(xreschar.toUpperCase()) > -1) {
                                                    foundstring = true;
                                                    break;
                                                }
                                            }
                                            if (foundstring && idata1 < idata) {
                                                continue;
                                            }
                                            xreschar = '';
                                            datastatus[idata].updated = true;
                                            foundmatch = true;
                                        }
                                    }
                                }
                            }
                            if (xreschar) {
                                for (idata = 0; idata < datastatus.length; idata++) {
                                    if (!datastatus[idata].updated && datastatus[idata].name.toUpperCase().indexOf(xreschar.toUpperCase()) > -1) {
                                        datastatus[idata].characts = datastatus[idata].name.toUpperCase().indexOf(xreschar.toUpperCase()) + xreschar.length;
                                        datastatus[idata].updated = true;
                                    }
                                }
                            }
                            xlength = 0;
                            for (idata = 0; idata < datastatus.length; idata++) {
                                if (datastatus[idata].updated) {
                                    datastatus[idata].updated = false;
                                    if (datastatus[idata].characts) {
                                        xlength += datastatus[idata].characts;
                                        continue;
                                    }
                                    xlength += datastatus[idata].name.length + 1;
                                    foundmatch = false;
                                    continue;
                                }
                                if (foundmatch) {
                                    datastatus[idata].updated = true;
                                }
                            }
                            xpos = 0;
                            for (idata = 0; idata < datastatus.length; idata++) {
                                if (datastatus[idata].updated) {
                                    xpos += datastatus[idata].name.length + 1;
                                }
                            }
                            yrpos = -1;
                            yrlength = -1;
                            if (yearsearch[displaycount].yrstatus) {
                                cval = autocompletevalue1.split(' ');
                                for (icval = 0; icval < cval.length; icval++) {
                                    if (yrsselected[displaycount].years.indexOf(cval[icval]) > -1) {
                                        yval = ', ' + yrsselected[displaycount].years;
                                        yrpos = yval.indexOf(', ' + cval[icval]);
                                        yrlength = cval[icval].trim().length;
                                        break;
                                    }
                                }
                            }
                        }
                        html = '<label id = "' + eid + '_' + displaycount + '">' + xdetails.substr(0, xpos) + '</label> ';
                        html += '<strong id = "' + eid + '_' + displaycount + '">' + xdetails.substr(xpos, xlength) + '</strong>';
                        html += ' <label id = "' + eid + '_' + displaycount + '">' + xdetails.substr(xpos + xlength) + '</label>';
                        if (yrpos == -1) {
                            html += '<p id = "' + eid + '_' + displaycount + '" style = "font-size:11px;color:#c6ae87">' + yrsselected[displaycount].years + '</p>';
                        } else {
                            html += '<p id = "' + eid + '_' + displaycount + '" style = "font-size:11px;color:#c6ae87">';
                            html += '<label>' + yrsselected[displaycount].years.substr(0, yrpos - 1) + '</label> ';
                            html += '<strong  id = "' + eid + '_' + displaycount + '">' + yrsselected[displaycount].years.substr(yrpos, yrlength) + '</strong>';
                            html += ' <label id = "' + eid + '_' + displaycount + '">' + yrsselected[displaycount].years.substr(yrpos + yrlength) + '</label>';
                            html += '</p>';
                        }
                        html += '<input  id = "' + eid + displaycount + 'value' + '" rel = "popval" type="hidden" value="' + escape(xdetails) + '">';
                        b.innerHTML = html;
                    } else {
                        html = xdetails;
                        yrs = ', ' + yrsselected[displaycount].years;
                        xpos = yrs.indexOf(', ' + autocompletevalue.toUpperCase());
                        html += '<p id = "' + eid + '_' + displaycount + '" style = "font-size:11px;color:#c6ae87">';
                        html += '<label id = "' + eid + '_' + displaycount + '">' + yrsselected[displaycount].years.substr(0, xpos) + '</label> ';
                        html += '<strong  id = "' + eid + '_' + displaycount + '">' + yrsselected[displaycount].years.substr(xpos, autocompletevalue.length) + '</strong>';
                        html += ' <label id = "' + eid + '_' + displaycount + '">' + yrsselected[displaycount].years.substr(xpos + autocompletevalue.length) + '</label>';
                        html += '</p>';
                        html += '<input  id = "' + eid + displaycount + 'value' + '" rel = "popval" type="hidden" value="' + escape(xdetails) + '">';
                        b.innerHTML = html;
                    }
                    b.addEventListener('mousedown', function (e) {
                        selval = $('#' + e.srcElement.id.split('_').join('') + 'value').val();
                        e.preventDefault();
                        e.stopPropagation();
                        if (!selval) {
                            return;
                        }
                        $('#' + e.srcElement.id.split('_')[0]).val(unescape(selval).split(' ').join(' '));
                        //           inp.value = unescape(selval).split("||").join(" ");
                        //              https://autogenie.co.uk/add-car/?car-brands=ford&serie=b-max&car-generations=b-max&trim=1-0-ecoboost-120-hp-start-stop
                    });
                    elem.appendChild(b);
                    displayopen = true;
                }
            }, 250);
        }

        function processlink(inp, selval) {
            if (!inp.value) {
                return;
            }
            var link = document.createElement('a');
            link.style.visibility = 'hidden';
            if (showdetailsinblankpage) {
                link.target = '_blank';
            }
            link.href =
                'https://autogenie.co.uk/add-car/?car-brands=' +
                unescape(selval).split(' ')[0] +
                '&serie=' +
                unescape(selval).split(' ')[1] +
                '&car-generations=' +
                unescape(selval).split(' ')[2] +
                '&trim=' +
                unescape(selval).split(' ')[3];
            link.click();
            link.remove();
        }

        async function getdata() {
            let response = await fetch('../../wp-admin/includes/awss3.php', { mode: 'cors' });
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        }

        function initsearch(data, inputfield, adjust) {
            finaldata = {};
            for (imake = 0; imake < data.brands.brand.length; imake++) {
                if (!data.brands.brand[imake].models.model || data.brands.brand[imake].models.model.length == 0) {
                    if (!finaldata[data.brands.brand[imake].name]) {
                        finaldata[data.brands.brand[imake].name] = [];
                    }
                    finaldata[data.brands.brand[imake].name].push(data.brands.brand[imake]);
                    continue;
                }
                for (imodel = 0; imodel < data.brands.brand[imake].models.model.length; imodel++) {
                    if (!data.brands.brand[imake].models.model[imodel].generations.generation || data.brands.brand[imake].models.model[imodel].generations.generation.length == 0) {
                        if (!finaldata[data.brands.brand[imake].name + ' ' + '']) {
                            finaldata[data.brands.brand[imake].name + '  ' + ''] = [];
                        }
                        finaldata[data.brands.brand[imake].name + ' ' + ''].push(data.brands.brand[imake].models.model[imodel]);
                        continue;
                    }
                    for (igenre = 0; igenre < data.brands.brand[imake].models.model[imodel].generations.generation.length; igenre++) {
                        if (
                            !data.brands.brand[imake].models.model[imodel].generations.generation[igenre].modifications.modification ||
                            data.brands.brand[imake].models.model[imodel].generations.generation[igenre].modifications.modification.length == 0
                        ) {
                            if (!finaldata[data.brands.brand[imake].name + ' ' + '' + data.brands.brand[imake].models.model[imodel].generations.generation[igenre].name]) {
                                finaldata[data.brands.brand[imake].name + ' ' + '' + data.brands.brand[imake].models.model[imodel].generations.generation[igenre].name] = [];
                            }
                            finaldata[data.brands.brand[imake].name + ' ' + '' + data.brands.brand[imake].models.model[imodel].generations.generation[igenre].name].push(
                                data.brands.brand[imake].models.model[imodel].generations.generation[igenre]
                            );
                            continue;
                        }
                        for (imodi = 0; imodi < data.brands.brand[imake].models.model[imodel].generations.generation[igenre].modifications.modification.length; imodi++) {
                            if (
                                !finaldata[
                                    data.brands.brand[imake].name +
                                        ' ' +
                                        '' +
                                        data.brands.brand[imake].models.model[imodel].generations.generation[igenre].name +
                                        ' ' +
                                        data.brands.brand[imake].models.model[imodel].generations.generation[igenre].modifications.modification[imodi].engine
                                ]
                            ) {
                                finaldata[
                                    data.brands.brand[imake].name +
                                        ' ' +
                                        '' +
                                        data.brands.brand[imake].models.model[imodel].generations.generation[igenre].name +
                                        ' ' +
                                        data.brands.brand[imake].models.model[imodel].generations.generation[igenre].modifications.modification[imodi].engine
                                ] = [];
                            }
                            finaldata[
                                data.brands.brand[imake].name +
                                    ' ' +
                                    '' +
                                    data.brands.brand[imake].models.model[imodel].generations.generation[igenre].name +
                                    ' ' +
                                    data.brands.brand[imake].models.model[imodel].generations.generation[igenre].modifications.modification[imodi].engine
                            ].push(data.brands.brand[imake].models.model[imodel].generations.generation[igenre].modifications.modification[imodi]);
                        }
                    }
                }
            }
            $('.autocomplete').css('display', 'block');
            end = new Date();
            timetaken = end - start;
            timetaken /= 1000;
            console.log('Time taken in seconds..' + Math.round(timetaken));
            autocompleted(document.getElementById(inputfield), inputfield, adjust);
        }

        function initfields() {
            var fields = $(document).find('input');
            for (ifield = 0; ifield < fields.length; ifield++) {
                if ($(fields[ifield]).attr('placeholder') && $(fields[ifield]).attr('placeholder').toUpperCase().indexOf('MAKE') > -1) {
                    if ($(fields[ifield])[0].clientHeight) {
                        $(fields[ifield]).attr('id', inputfield);
                    }
                }
            }
            $('.dropdown-menu-custom').attr('id', 'carsearchbutton');
            $('#' + inputfield).attr('autocorrect', 'off');
            $('#' + inputfield).attr('autocomplete', 'off');
        }
        maindata = null;
        start = new Date();
        function initacomplete(inputfield, dataprocess, adjust) {
            document.getElementById(inputfield).addEventListener('focus', function (e) {
                focussed = e.srcElement.id;
            });
            if (!dataprocess) {
                $(document).on('change', '#' + inputfield + '-select', function (e) {
                    e.preventDefault();
                    e.stopPropagation();
                    datafound = false;
                    for (idata = 0; idata < dtsselected.length; idata++) {
                        if (dtsselected[idata].name.split(' ').join(' ').toUpperCase() === document.getElementById($(this)[0].id.split('-')[0]).value.toUpperCase()) {
                            datafound = true;
                            break;
                        }
                    }
                    if (datafound) {
                       // processlink(document.getElementById($(this)[0].id.split('-')[0]), selval);
                    }
                });
                autocompleted(document.getElementById(inputfield), inputfield, adjust);
                return;
            }
            getdata()
                .then((data) => {
                    setTimeout(function () {
                        //          initfields()
                        setTimeout(function () {
                            $('.autocomplete-items').css('height', $(window).height() * 0.25 + 'px');
                            $('.autocomplete-items').css('width', $('#' + inputfield).width() + 20 + 'px');
                        }, 200);
                        maindata = data;
                        $(document).on('change', '#' + inputfield + '-select', function (e) {
                            e.preventDefault();
                            e.stopPropagation();
                            datafound = false;
                            try {
                                for (idata = 0; idata < dtsselected.length; idata++) {
                                    if (dtsselected[idata].name.split(' ').join(' ').toUpperCase() === document.getElementById($(this)[0].id.split('-')[0]).value.toUpperCase()) {
                                        datafound = true;
                                        break;
                                    }
                                }
                            } catch (e) {
                                $('#' + $(this)[0].id.split('-')[0]).click();
                            }
                            if (datafound) {
                              //  processlink(document.getElementById($(this)[0].id.split('-')[0]), selval);
                            }
                        });

                        initsearch(data, inputfield, adjust);
                    }, 1500);
                })
                .catch((e) => console.log(e));
        }

        setTimeout(function () {
            console.log('hot');
            new initacomplete('carsearch1', true, 0);
        }, 1000);

        //setTimeout(function(){
        //   new initacomplete("carsearch1-m",false,0);
        //},1500)

        //setTimeout(function(){
        //    new initacomplete("carsearchfooter",false,40);
        //},1500)


        $('#car-search-btn').on('click', function (e) {
            e.preventDefault();
            var ex_search_field_value = $('#carsearch1').val(),
                ex_dropdown_selected = $(this).siblings('.c-col-1').find('.nice-select > .current').text(),
                car_data = finaldata[ex_search_field_value],
                base_url = 'https://autogenie.co.uk/';
                console.log(ex_dropdown_selected);
                if (ex_search_field_value.length > 0) {
    
                    if (car_data) {
                        var slug = ex_dropdown_selected == 'Sell' ? 'buyer-list/?' : 'request-a-car/?';
    
                        var query = 'car-brands=' + car_data[0].brand.replace(/\W+/g, '-').toLowerCase()
                            + '&serie=' + car_data[0].model.replace(/\W+/g, '-').toLowerCase()
                            + '&car-generations=' + car_data[0].generation.replace(/[^a-zA-z0-9\.,]/g, '-').toLowerCase()
                            + '&trim=' + car_data[0].engine.replace(/\W+/g, '-').toLowerCase();
                        var redirected_to = base_url + slug + query;
    
                        window.location.href = redirected_to;
                    } else {
                        alert(base_url + slug + query);
                    }
                } else {
                    alert('Please enter car data');
                }


        });


        $('#car-search-btn-svg').on('click', function (e) {
            e.preventDefault();
            var exp_search_field_value = $('#carsearch1').val(),
                exp_dropdown_selected = $(this).siblings('.choose-menu-custom').find('input[name=choose-buy-sell]:checked').val(),
                exp_car_data = finaldata[exp_search_field_value],
                exp_base_url = 'https://autogenie.co.uk/';
            console.log(exp_dropdown_selected);
            if (exp_search_field_value.length > 0) {

                if (exp_car_data) {
                    var exp_slug = exp_dropdown_selected == 'sell-car' ? 'buyer-list/?' : 'request-a-car/?';

                    var exp_query = 'car-brands=' + exp_car_data[0].brand.replace(/\W+/g, '-').toLowerCase()
                        + '&serie=' + exp_car_data[0].model.replace(/\W+/g, '-').toLowerCase()
                        + '&car-generations=' + exp_car_data[0].generation.replace(/\W+/g, '-').toLowerCase()
                        + '&trim=' + exp_car_data[0].engine.replace(/\W+/g, '-').toLowerCase();
                    var exp_redirected_to = exp_base_url + exp_slug + exp_query;
                    console.log(exp_redirected_to);
                    window.location.href = exp_redirected_to;
                } else {
                    alert('No data found');
                }
            } else {
                alert('Please enter car data');
            }
        });
    });
})(jQuery);