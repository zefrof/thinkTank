var i = 0;

function duplicate() {
    var og = document.getElementById("deck");
    var clone = og.cloneNode(true);

    clone.id = "deck" + ++i;
    
    var inputs = clone.getElementsByTagName('input');
    for(var k = 0; k < inputs.length; k++) {
        inputs[k].id += i;
        inputs[k].name += i;
        inputs[k].value = '';
    }

    var sel = clone.getElementsByTagName('select');
    for(var k = 0; k < sel.length; k++) {
        sel[k].id += i;
        sel[k].name += i;
    }

    var textareas = clone.getElementsByTagName('textarea');
    for(var k = 0; k < textareas.length; k++) {
        textareas[k].id += i;
        textareas[k].name += i;
        textareas[k].value = '';
    }

    og.parentNode.appendChild(clone);

    document.getElementById("deckNumber").value = i;
}

function xhrHandler(form) {
	var xhr = new XMLHttpRequest();
	//xhr.onload = function() { }
	xhr.open(form.method, form.action);
	xhr.send(new FormData (form)); 

    console.log("Done");

	return false;
}

function xhrAjax(arch, format) {
   /*  console.log(arch);
    console.log(format); */

    var xhr = new XMLHttpRequest();
    xhr.open("GET", "../tournament/ajax.event.php?arch=" + arch + "&format=" + format);
    xhr.onreadystatechange = function() {
        if (this.readyState !== 4) return;
        if (this.status !== 200) return; //error handling
        //console.log(this.responseText);
        document.getElementById('content').innerHTML = this.responseText;
    };
    xhr.send()
}

function deckAjax(id) {
    /*  console.log(arch);
     console.log(format); */
 
     var xhr = new XMLHttpRequest();
     xhr.open("GET", "../tournament/ajax.event.php?action=editEvent&id=" + id);
     xhr.onreadystatechange = function() {
         if (this.readyState !== 4) return;
         if (this.status !== 200) return; //error handling
         //console.log(this.responseText);
         document.getElementById('content').innerHTML = this.responseText;
     };
     xhr.send()
 }