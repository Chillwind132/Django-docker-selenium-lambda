function waitForElement(){
    if(typeof done_var !== "undefined"){
        location.href = "http://3.82.199.161/redirect";
        setTimeout(() => {  location.href = "http://3.82.199.161"; }, 500);
        console.log("Redirect triggered - log");
    }
    else{
        setTimeout(waitForElement, 250);
    }
}
/*
http://127.0.0.1:8000/
    
*/