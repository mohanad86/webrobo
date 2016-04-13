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

setInterval(function(){ 
    $.getJSON('/batterycharge', function(data) {
        console.info(data);
        $("#batterystats").text(data.power/1000000 + "watts");
    });
    }, 3000);
 
