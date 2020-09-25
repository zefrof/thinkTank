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

function getSubArk(arkId, id) {
	//console.log(arkId);

	if(arkId === "None") {
		return;
	}

	$.ajax({
		method: "POST",
		datatype: 'json',
		data: { arkId: arkId },
		url: '/getsubark/',
		success: function(response) {
			//console.log(response);
			var subArks = JSON.parse(response);

			var select = document.getElementById(id);
			select.options.length = 0; //possible memory leak?
			//Add a blank one so it can be selected
			var opt = document.createElement('option');
			opt.value = 0;
			select.appendChild(opt);
			for(i = 0; i < subArks.length; i++) {
				var opt = document.createElement('option');
				opt.value = subArks[i][0];
				opt.innerHTML = subArks[i][1];
				select.appendChild(opt);
			}
		}
	});
}

function loadMore(day, fid = 0) {
	$.ajax({
		method: "POST",
		datatype: 'json',
		data: { day: day, fid: fid },
		url: '/loadmore/',
		success: function(response) {
			var events = JSON.parse(response);
			console.log(events['events']);

			//Decide if half matters or not
			//Update arguments for loadMore()
			if(fid == 0) {
				var half = Math.floor(events['events'].length / 2);
				document.getElementById( "loadMore" ).setAttribute( "onClick", "loadMore('" + events['events'][0]['date'] + "');" );
			} else {
				var half = events['events'].length + 1;
				document.getElementById( "loadMore" ).setAttribute( "onClick", "loadMore('" + events['events'][0]['date'] + "', '" + fid + "');" );
			}
			
			var target = "col1";
			
			for(var i = 0; i < events['events'].length; i++) {
				if(i >= half) {
					target = "col2";
				}
				
				//Event name
				var div = document.createElement('div');
				div.classList = "cell large-6";
				var h4 = document.createElement('h4');
				h4.classList = "homeList";
				var a = document.createElement('a');
				a.href = '/deck/' + events['events'][i]['firstPlaceDeckId'];
				a.innerText = events['events'][i]['name'];
				h4.appendChild(a);
				div.appendChild(h4);
				document.getElementById(target).appendChild(div);

				//Number of players
				div = document.createElement('div');
				div.classList = "cell large-2"
				var p = document.createElement('p');
				p.innerText = events['events'][i]['numPlayers'];
				div.appendChild(p);
				document.getElementById(target).appendChild(div);

				//Date
				div = document.createElement('div');
				div.classList = "cell large-4";
				p = document.createElement('p');
				p.innerText = events['events'][i]['date'];
				div.appendChild(p);
				document.getElementById(target).appendChild(div);
			}			
		}
	});
}