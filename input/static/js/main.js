function waitForElement(){
    if(typeof done_var !== "undefined"){
        location.href = 'http://52.201.219.127/redirect';
        window.location.href = "http://52.201.219.127"; 
        /*window.open("http://52.201.219.127/redirect", '_blank');*/
        console.log("Redirect triggered - log");
    }
    else{
        setTimeout(waitForElement, 250);
    }
}

/*

http://127.0.0.1:8000/
    
*/
