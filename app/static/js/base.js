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
    if (checkBox.checked == true){
        document.getElementById("div_gifted_data").style.display = "inline";
    } else {
        document.getElementById("div_gifted_data").style.display = "none";
    }
}