function changeDeck(deckId) {
    //console.log(deckId);
    window.location.href = '/deck/' + deckId;
}

function showImage(imgUrl, altText, price = '0.00', foilPrice = '0.00') {
	//console.log(imgUrl);
	document.getElementById('imageSrc').src = imgUrl;
	document.getElementById('imageSrc').alt = altText;
	
	//console.log(price);
	if(price === '0.00') {
		document.getElementById('price').innerText = 'Not Available';
	} else {
		document.getElementById('price').innerText = price + '$';
	}

	if(foilPrice === '0.00') {
		document.getElementById('foilPrice').innerText = 'Not Available';
	} else {
		document.getElementById('foilPrice').innerText = foilPrice + '$';
	}
}