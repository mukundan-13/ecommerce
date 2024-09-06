let currentColor = 'color1'; // Default color
const maxQuantity = 5;

function changeImage(imageSrc) {
    document.getElementById('main-image').src = imageSrc;
}

function changeColor(color) {
    currentColor = color;
    var image=document.getElementById("main-image")
    image.src="ecom/bshoe1.jpeg" 
    var i1=document.getElementById("i1")
    i1.src="ecom/bshoe1.jpeg" 
    i1.onclick=function()
    {
        changeImage('ecom/bshoe1.jpeg')
    }
    var i2=document.getElementById("i2")
    i2.src="ecom/bshoe2.jpeg"
    i2.onclick=function()
    {
        changeImage('ecom/bshoe2.jpeg')
    }
    var i3=document.getElementById("i3")
    i3.src="ecom/bshoe3.jpeg"
    i3.onclick=function()
    {
        changeImage('ecom/bshoe3.jpeg')
    }
    console.log(`Color changed to ${color}`);
}

function addToCart() {
    const quantity = parseInt(document.getElementById('quantity').value, 10);
    if (quantity < 1 || quantity > maxQuantity) {
        document.getElementById('cart-message').innerText = `You can only add up to ${maxQuantity} items to the cart.`;
    } else {
        document.getElementById('cart-message').innerText = `${quantity} item(s) added to cart.`;
    }
}
