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
    console.log("Done");
    var response = xmlhttp.response;
    console.log(response);
    document.getElementById('first').textContent = response;
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
            }
        },
        function(errorMessage)
        {
              console.log('Cannot display image. ' + errorMessage);
        }

    );
});