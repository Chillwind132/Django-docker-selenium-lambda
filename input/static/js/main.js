function waitForElement(){
    if(typeof done_var !== "undefined"){
        location.href = "http://52.201.219.127/redirect";
        setTimeout(() => {  location.href = "http://52.201.219.127"; }, 500);
        console.log("Redirect triggered - log");
    }
    else{
        setTimeout(waitForElement, 250);
    }
}
/*
http://127.0.0.1:8000/
    
*/