function waitForElement(){
    if(typeof done_var !== "undefined"){
        location.href = "/redirect";
        setTimeout(() => {  location.href = "/"; }, 500);
        console.log("Redirect triggered - log");
    }
    else{
        setTimeout(waitForElement, 250);
    }
}
