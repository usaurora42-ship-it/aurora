function StoreUserState(stateName, stateValue, expiryDays = 0){
    //Create a date object set to the current time.
    const currentDate = new Date();
    if (expiryDays > 0){
        currentDate.setTime(currentDate.getTime() + (expiryDays * 24 * 60 * 60 * 1000));
    }

    const expires = "expires=" + currentDate.toUTCString();

    //Build the cookie string with
    //name, value, expiration, and path.
    const cookieString = `${stateName}=${stateValue}${expires};path=/`;

    //Set the cookie using document.cookie
    document.cookie = cookieString;
}

function retrieveUserState(stateName){
    const name = stateName + "=";
    const decodedCookie = decodeURIComponent(document.cookie);
    const stateEntries = decodedCookie.split(';');
    for (let i = 0; i < stateEntries.length; i++){
        let stateEntry = stateEntries[i];
        while (stateEntry.charAt(0) === ' '){
            stateEntry = stateEntry.substring(1);
        }
        if (stateEntry.indexOf(name) === 0){
            return stateEntry.substring(name.length, stateEntry.length);
        }
    }
    return "";
}
StoreUserState("userSession ", "loggedIn ", 1);
const userState = retrieveUserState("userState")
console.log("Session value: ", userState);

StoreUserState("pizza ", "tast ", 2);
console.log("Session value: ", userState);