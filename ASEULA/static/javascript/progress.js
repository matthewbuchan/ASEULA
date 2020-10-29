function Show_Progress() {
    var progressbar = document.getElementById("progress-bar");
    var disablebutton = document.getElementById("submission-btn");
    var filebutton = document.getElementById("file-input");
    var textbutton = document.getElementById("text-input");

    if (progressbar.style.display = "none") {
        progressbar.style.display = "block";
    }

    disablebutton.disabled = true;
    filebutton.disabled = true;
    textbutton.disabled = true;
  }

  function Export_Disable_Button() {
    var exportbutton = document.getElementById("export-btn");
    exportbutton.disabled = true;
  }