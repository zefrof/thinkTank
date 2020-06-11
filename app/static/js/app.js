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

function getSubArk(arkId) {
	//console.log(arkId);

	$.ajax({
		method: "POST",
		datatype: 'json',
		data: { arkId: arkId },
		url: '/getsubark/',
		success: function(response) {
			//console.log(response);
			subArks = JSON.parse(response);

			var select = document.getElementById('subArchetype');
			select.options.length = 0; //possible memory leak?
			for(i = 0; i < subArks.length; i++) {
				var opt = document.createElement('option');
				opt.value = subArks[i][0];
				opt.innerHTML = subArks[i][1];
				select.appendChild(opt);
			}
		}
	});
}