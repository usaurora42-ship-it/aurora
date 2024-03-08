$(function () {
     $('input[type="phone"]').mask('(00) 00000-0000')
     $('input[type="gifted_phone"]').mask('(00) 00000-0000')
     $('input[type="zip_code"]').mask('00000-000')
});

var dropdown = document.getElementById("typeperson");
dropdown.onchange = function(event){
    if(dropdown.value=="pf"){
        $('input[type="document"]').mask('000.000.000-00')
    }
    if(dropdown.value=="pj"){
        $('input[type="document"]').mask('00.000.000/0000-00')
    }
};

function msgcheckFunction(){
    var checkBox = document.getElementById("msgcheck");

    var text = document.getElementById("text");

    if (checkBox.checked == true){
        document.getElementById("gifted_data").style.visibility = "visible";
        document.getElementById("gifted_name").style.visibility = "visible";
        document.getElementById("gifted_phone").style.visibility = "visible";
        document.getElementById("gifted_ocasion").style.visibility = "visible";
        document.getElementById("gifted_message").style.visibility = "visible";
        document.getElementById("signature_card").style.visibility = "visible";
        document.getElementById("gifted_name").required = true;
    } else {
        document.getElementById("gifted_data").style.visibility = "hidden";
        document.getElementById("gifted_name").style.visibility = "hidden";
        document.getElementById("gifted_phone").style.visibility = "hidden";
        document.getElementById("gifted_ocasion").style.visibility = "hidden";
        document.getElementById("gifted_message").style.visibility = "hidden";
        document.getElementById("signature_card").style.visibility = "hidden";
        document.getElementById("gifted_name").required = false;
    }
}