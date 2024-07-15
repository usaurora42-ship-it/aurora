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
};

function checkuserFunction(){
    var checkBox = document.getElementById("checkuser");
    if (checkBox.checked == true){
        document.getElementById("div_gifted_user").style.display = "inline";
    } else {
        document.getElementById("div_gifted_user").style.display = "none";
    }
};

function previewImagem(event) {
    const imagemPreview = document.getElementById('imagem-preview');    
    imagemPreview.src = URL.createObjectURL(event.target.files[0]);
    imagemPreview.style.display = 'block';
};


