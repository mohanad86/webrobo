function loadDoc() {
  var xhttp;
  if (window.XMLHttpRequest) {
    xhttp = new XMLHttpRequest();
    } else {
    xhttp = new ActiveXObject("robot.html");
  }
  xhttp.onreadystatechange = function() {
    if (xhttp.readyState == 4 && xhttp.status == 200) {
      document.getElementById("java").innerHTML = xhttp.responseText;
    }
  };
  xhttp.open("GET", "ajax_info.txt", true);
  xhttp.send();
}
function removeMobileOnclick() {
    if(isMobile()) {
        document.querySelector('.mobile-head-bar-left').onclick  = '';
    }
}
//this will work for every phone
function isMobile() {
    if (navigator.userAgent.match(/Android/i)
            || navigator.userAgent.match(/iPhone/i)
            || navigator.userAgent.match(/iPad/i)
            || navigator.userAgent.match(/iPod/i)
            || navigator.userAgent.match(/BlackBerry/i)
            || navigator.userAgent.match(/Windows Phone/i)
            || navigator.userAgent.match(/Opera Mini/i)
            || navigator.userAgent.match(/IEMobile/i)
            ) {
        return true;
    }
}
window.addEventListener('load', removeMobileOnclick);

$('button').bind('touchstart', function(){
    $(this).addClass('button');
}).bind('touchend', function(){
    $(this).removeClass('button');
});

$('button').click(function () {
  $(this).css('button', '1px solid blue');
  $('button#red').css('button', '1px solid white');
});
//calling the function of the battery status
setInterval(function(){ 
    $.getJSON('/batterycharge', function(data) {
        console.info(data);
        $("#batterystats").text(data.power/1000000 + "watts");
        $("#voltage").text(data.voltage/1000000 + "voltage");
        $("#rightsensor").text(data.enemy_right + "rightsensor");
        $("#leftsensor").text(data.enemy_left + "leftsensor");
         });
    }, 3000); 
    
var nua = navigator.userAgent;
var is_android = ((nua.indexOf('Mozilla/5.0') > -1 && nua.indexOf('Android ') > -1 &&     nua.indexOf('AppleWebKit') > -1) && !(nua.indexOf('Chrome') > -1));
//disable the text selection
$.fn.extend({
    disableSelection: function() {
        this.each(function() {
            this.onselectstart = function() {
                return false;
            };
            this.unselectable = "on";
            $(this).css('-moz-user-select', 'none');
            $(this).css('-webkit-user-select', 'none');
        });
        return this;
    }
});

$(function() {
  $(this).disableSelection();
});
   
