function waitForElement(){
    if(typeof done_var !== "undefined"){
        window.location.href = "http://127.0.0.1:8000";
        window.open("http://127.0.0.1:8000/redirect", '_blank');
    }
    else{
        setTimeout(waitForElement, 250);
    }
}
