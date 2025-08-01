$(function () {
     $('input[type="phone"]').mask('(00) 00000-0000')
     $('input[type="gifted_phone"]').mask('(00) 00000-0000')
     $('input[type="zip_code"]').mask('00000-000')
});

/* var dropdown = document.getElementById("typeperson");
dropdown.onchange = function(event){
    if(dropdown.value=="pf"){
        $('input[type="document"]').mask('000.000.000-00')
    }
    if(dropdown.value=="pj"){
        $('input[type="document"]').mask('00.000.000/0000-00')
    }
}; */

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


function addBasket(qtdBasket){ 
    const countBasket = parseInt(qtdBasket) + 1;
    let qtdB = document.getElementById('qtdBasket');
    qtdB.value = countBasket;
    document.getElementById('qtdCart').value = qtdB.value;  
};

function remBasket(qtdBasket){ 
    const countBasket = parseInt(qtdBasket) - 1;
    let qtdB = document.getElementById('qtdBasket');    
    qtdB.value = countBasket; 
    document.getElementById('qtdCart').value = qtdB.value;  
};

/* function addCart(qtdBasket){
    const countBasket = parseInt(qtdBasket);
    let qtdB = document.getElementById('qtdBasket');    
    qtdB.value = countBasket; 
    document.getElementById('qtdCart').value = qtdB.value;   
} */

//Adiciona item ao carrinho (cookie)
function addCart(id, quantity = 1){ 
      let cart = JSON.parse(getCookie('cart') || '{}');
      cart[id] = (cart[id] || 0) + 1; 
      /* if (cart[idProduct]){
        cart[idProduct] += quantity;
      } else {
        cart[idProduct] = quantity;
      } */
      document.cookie = `cart=${JSON.stringify(cart)};path=/`;
      alert('Produto adicionado!'); 
};

function getCookie(name){
    const match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
    return match ? decodeURIComponent(match[2]) : null;
}

function showCart() {
    fetch('/cart')
    //.then(resp => resp.json())
    //.then(data => {
      //   const cart = document.getElementById('cart');
         /* if (data.length === 0){
            cart.innerHTML = '<div class="alert alert-warning">Carrinho vazio</div>';
            return;
         }
         let html = '<h3>Carrinho</h3><ul class="list-group">';
         let total = 0;
         data.forEach(item => {
           html += `<li class="list-group-item d-flex justify-content-between align-items-center">
              ${item.name} x ${item.quantity};  
              <span class="badge bg-primary">R$ ${item.subtotal.toFixed(2)}</span>  
           </li>`;            
           total += item.subtotal;
         });
         html += `</ul><h4 class="mt-3">Total: R$ ${total.toFixed(2)}</h4>`;
         cart.innerHTML = html; */
       // });
}