let links = document.getElementById("navbarSupportedContent").getElementsByTagName("a");

for (let index = 0; index < links.length; index++) {
  
  links[index].addEventListener("click", function(event) {
    event.preventDefault();

    if (!links[index].classList.contains("dropdown-toggle")) {
      let url = links[index].pathname;
      window.history.replaceState(null, "", url);
      document.title = "ZOTT-IT - " + url.slice(1, url.length);
      document.getElementById("header-menu-button").click();

      if(links[index].parentElement.previousElementSibling === null) {

        for (let x = 0; x < links.length; x++) {
          if(links[x].classList.contains("active")) {
            links[x].classList.remove("active");
            break;
          }
        }
        links[index].classList.add("active");

      } else {

        for (let x = 0; x < links.length; x++) {
          if(links[x].classList.contains("active")) {
            links[x].classList.remove("active");
            break;
          }
        }
        links[index].parentElement.previousElementSibling.classList.add("active");

      }

      getTemplate(url);
    }
  });
  
}

function getTemplate(path) {

  if(undefined === path) {
    path = "/info";
  }

  let xhr = new XMLHttpRequest();
  xhr.open("GET",  "/html" + path + ".html");
  xhr.addEventListener('load', function() {
    if(xhr.status >= 200 && xhr.status < 300) {
      if ("/update_successful" === path) {
        document.body.innerHTML = this.responseText;

        if(document.body.getElementsByTagName("script").length > 0) {
          eval(document.body.getElementsByTagName("script")[1].innerText)
        }
      } else {
        document.getElementById("content").innerHTML = this.responseText

        if(document.getElementById("content").getElementsByTagName("script").length > 0) {
          eval(document.getElementById("content").getElementsByTagName("script")[0].innerText)
        }
      }
    }
  })
  xhr.send();
}

function getInfos(func, args) {
  // getTimeDate()
  getFWversion()

  if (func != null) {
      if (args != null) {
          console.log(args);
          func(args)
      } else {
          func()
      }
  }
}

function getFWversion() {
  xhttp = new XMLHttpRequest()
  xhttp.onreadystatechange = function() {
      if (this.readyState == 4 && this.status == 200) {
        for (let index = 0; index < document.getElementsByClassName('FWversion').length; index++) {
          document.getElementsByClassName('FWversion')[index].innerHTML = this.responseText
        }
      }
  }
  xhttp.open("GET", '/FWversion', true)
  xhttp.send()
}

function getTimeDate() {
  let date = new Date();

  let timezone = new Date();
  timezone = timezone.toTimeString();
  timezone = timezone.slice(12,15);

  let day = new Intl.DateTimeFormat('en', {day: '2-digit'}).format(date);
  let month = new Intl.DateTimeFormat('en', {month: '2-digit'}).format(date)

  document.getElementById('timeDate').innerHTML = date.getFullYear() + "-" + month + "-" + day + " " + date.toLocaleTimeString("de-DE") + " UTC" + timezone;
}