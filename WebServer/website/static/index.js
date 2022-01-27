function checkBoxSelected(number) {
    fetch("/select", {
      method: "POST",
      body: JSON.stringify({ number: number }),
    }).then((response) => response.json()) 
      .then((obj) => { 
      if(obj.erro === 1){
        window.location.href = "/error";
      }else{
        window.location.href = "/";
      }
    });
  }

  function deleteDatabase() {
    fetch("/deletedb", {
      method: "POST",
      body: JSON.stringify({ }),
    }).then((response) => response.json()) 
      .then((obj) => {
      if(obj.erro === 1){
        window.location.href = "/error";
      }else{
        window.location.href = "/admin";
      }
    });
  }

  function status() {
    fetch("/status", {
      method: "POST",
      body: JSON.stringify({ }),
    }).then((response) => response.json()) 
      .then((obj) => {
      if(obj.erro === 1){
        window.location.href = "/error";
      }else{
        window.location.href = "/payment";
      }
    });
  }