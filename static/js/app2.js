
function addCamera() {
  var camURL = document.getElementById("camURL").value;
 
  alertstyle = "alert-success";
  var icon = '<i class="fa fa-video-camera fa-3x" aria-hidden="true"></i>'

  $.ajax({
        type: "POST",
        url: "{{ url_for('add_camera') }}",
        data : {'camURL': camURL},
        success: function(cam) {
          console.log(cam);
              var camdiv = document.createElement("div");
              camdiv .setAttribute("class","alert alert-dismissable " + alertstyle);   
              var btn = document.createElement("BUTTON");        
              btn.setAttribute("type","button");    
              btn.setAttribute("class", "close"); 
              btn.setAttribute("data-dismiss", "alert");  
              btn.setAttribute("aria-hidden","true"); 
              btn.setAttribute("onclick","removeCamera(this.id)"); 
              btn.setAttribute("id","camera_" + cam.camNum);
              btn.innerHTML = "&times;";
              camdiv.innerHTML = '<div class="text-center"><span>' + icon + '<div><strong>Camera '+ cam.camNum + ' FPS: <strong id="camera_' + cam.camNum+ '_fps">' + "Loading... </strong></div><div>" +'<font size="0.9">' + camURL+'<font></span></div>';
              camdiv.appendChild(btn);
              document.getElementById("system-cameras").appendChild(camdiv);
              var viddiv = document.createElement("div");
              viddiv.setAttribute("class","col-md-4 col-sm-6 col-xs-12");  
              var vidstream = document.createElement("img");
              vidstream.setAttribute("class","img-thumbnail panel panel-default"); 
              vidstream.setAttribute("id",cam.camNum); 
              vidstream.setAttribute("src","/video_streamer/" + cam.camNum); 
              vidstream.setAttribute("width","540"); 
               vidstream.setAttribute("height","320");
              viddiv.appendChild(vidstream);
              document.getElementById("surveillance_panel").appendChild(viddiv);
              $('#addcam').html('Add Camera');
        },
        error: function(error) {
          console.log(error);
        }
  });
  
}

function reloadThePage(){
  window.location.reload();
} 

// --------------------- socket connection jquery and java code ------------------------------------
var old_data = {};
$(document).ready(function(){
    //connect to the socket server.
    var socket = io.connect('http://' + document.domain + ':' + location.port + '/test');

    //receive details from server
    socket.on('people_detected', function(json) {
        var people = JSON.parse(json);
        console.log("Received peopledata in Loop" + people);
        var length = people.length
        console.log('length of data = ' + length);
        console.log('length of old data = ' + old_data['length']);
        people_string = '';
        old_data['length'] = length
        if (people.lenght != 0) {
          // window.location.reload(false);
        }
        
        for (var i = 0; i < people.length; i++){
            facename = people[i].facename;
            username = people[i].username;
            punch = people[i].punch;
            date_time = people[i].date_time;
            console.log("facename " + facename);
            if(!document.getElementById(facename)){
            var img = $('<img />', { 
                id: facename,
                src: '/static/capturedfaces/' + facename,
                width :'130px',
                height:'142px'
              });
              var usernametag = $('<p />', { 
                id: username,
                text:"Username : " + username
              });
              var punchtag = $('<p />', { 
                id: username,
                text:"Punch : " + punch
              });
              var date_timetag = $('<p />', { 
                id: username,
                text:"DateTime : " + date_time
              });

              if (username == "Unknown") {
                var btn = $('<button/>',{
                  text: 'Register',
                  click: function () { alert('function call'); }
              });
                img.appendTo($('#unknown'));
                usernametag.appendTo($('#unknowndata'));
                btn.appendTo($('#unknowndata'));
              } else {
                img.appendTo($('#log'));
                usernametag.appendTo($('#data'));
                punchtag.appendTo($('#data'));
                date_timetag.appendTo($('#data'));   
              }
            }
        }  
        // window.location.reload(false);      
    });

});