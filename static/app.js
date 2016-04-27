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
        $("#batterystats").text(data.power/1000000 + " Watts ");
        $("#voltage").text(data.voltage/1000000 + " Voltage ");
        $("#rightsensor").text(data.enemy_right + " Rightsensor ");
        $("#rightsensor").toggleClass("activated", data.enemy_right == 1);
        $("#leftsensor").text(data.enemy_left + " Leftsensor ");
        $("#leftsensor").toggleClass("activated", data.enemy_left == 1);
        $("#capacity").text(data.capacity + "% power");
        $("#charge").css("width", data.capacity + "%");
        // variable 'data' does not exist after this
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


$("html").keydown(function(e) {
    e.preventDefault();
    switch (e.keyCode) {
        case 37:
            $.get('/left');
            console.info("Pressed left?");
            break
        case 39:
			$.get("/right");
            console.info("Pressed right");
            break;
        case 38:
            $.get("/go");
            break;
         case 40:
            $.get("/back");
        default:
        		$("#msg").html("Pressed unknown button");
            console.info("User pressed uknown button with keycode:", e.keyCode);
    }
    return false;
});

$("html").keyup(function(e) {
    $.get("/stop");
    e.preventDefault(); // Prevent page from scrolling
    return false;
});


  
