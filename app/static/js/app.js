function changeDeck(deckId) {
    //console.log(deckId);
    window.location.href = '/deck/' + deckId;
}

function showImage(imgUrl, altText) {
	//console.log(imgUrl);
	document.getElementById('imageSrc').src = imgUrl;
	document.getElementById('imageSrc').alt = altText;
}