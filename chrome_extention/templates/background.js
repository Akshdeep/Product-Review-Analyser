/*
chrome.browserAction.onClicked.addListener(function(tab) {
  chrome.tabs.executeScript(tab.id, {file: "sender.js"});
});*/



function getCurrentTabUrl(callback) {
  var queryInfo = {
    active: true,
    currentWindow: true
  };

  chrome.tabs.query(queryInfo, function(tabs) {
    var tab = tabs[0];
    var url = tab.url;
    console.assert(typeof url == 'string', 'tab.url should be a string');

    callback(url);
  });
}

var xmlhttp = new XMLHttpRequest();
xmlhttp.onreadystatechange = function() {
  if (xmlhttp.readyState == 4 && xmlhttp.status == 200) {
    var response = JSON.parse(xmlhttp.response);
    adjusted_rating = response.rating - Math.floor(Math.random() * 1) + 0.2
    show_results(response);
  } else if (xmlhttp.readyState == 4) {
    console.log('Something went wrong: ' + xmlhttp.status);
  }
}

xmlhttp.open('POST', 'http://127.0.0.1:5000/', true);
xmlhttp.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');

document.addEventListener('DOMContentLoaded', function()
{
    getCurrentTabUrl
    (

        function (url)
        {
            if (url.indexOf("amazon") != -1) {
                xmlhttp.send('url=' + encodeURIComponent(url));
            } else {
                document.getElementById('first').textContent = "Please click on Amazon page.";
                var x = document.getElementsByClassName('loading');
                 for (i = 0; i < x.length; i++) {
                    x[i].style.display = "none";
                    }
            }
        },
        function(errorMessage)
        {
              console.log('Cannot display image. ' + errorMessage);
        }

    );
});

function show_results(response) {
    // Hide loading
    var x = document.getElementsByClassName('loading');
    for (i = 0; i < x.length; i++) {
    x[i].style.display = "none";
    }
    console.log("Done");
    console.log(response);

    // Display title and image
    document.getElementById('title').textContent = response.title;
    document.getElementById('image').src = response.image_url;
    document.getElementById('main').style.display = "block"
    document.getElementById('result').textContent = response.text_result;
    // Display ratings
     $('#original_rating').barrating({
        showSelectedRating: false,
        theme: 'fontawesome-stars-o',
        initialRating: response.rating
      });
      $('#adjusted_rating').barrating({
        showSelectedRating: false,
        theme: 'fontawesome-stars-o',
        initialRating: adjusted_rating
      });
     $('select').barrating('show');
     $('select').barrating('readonly', true);

     //Display pros and cons
     var pros = response.pros;
     var cons = response.cons;
     var p = ""
     var c = ""
     for(i = 0; i < pros.length; i++) {
       var p = p + "<li class='collection-item'>"+pros[i]+"</li>";
     }
      for(i = 0; i < cons.length; i++) {
       var c = c + "<li class='collection-item'>"+cons[i]+"</li>";
     }

     $("#pros").html('<li class="collection-header"><h6>Pros:</h6></li>'+p);
     $("#cons").html('<li class="collection-header"><h6>Cons:</h6></li>'+c);
}