function waitForElement(){
    if(typeof done_var !== "undefined"){
        window.location.href = "http://127.0.0.1:8000/redirect";
    }
    else{
        setTimeout(waitForElement, 250);
    }
}
