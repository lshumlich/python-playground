var toggle = 0

function doSomething(event) {
	if (toggle == 0){
		toggle = 1;
		document.getElementById('image').src = 'pic_mountain.jpg';
	} else {
		toggle = 0;
		document.getElementById('image').src = 'html5.gif';
	}
	var msg = ""
	msg += ' sx=' + event.screenX;                    // Update element with screenX
  	msg += ' sy=' + event.screenY;                    // Update element with screenY
	el = document.getElementById('concole');
	el.innerHTML = msg;
}

document.getElementById('link').addEventListener('click', doSomething,false)

