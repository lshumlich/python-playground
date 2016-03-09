
//-------- Top nav bar -----------

var adminEl = document.getElementById("admin");
var infrastructureEl = document.getElementById("infrastructure");
var dataEl = document.getElementById("data");
var consoleEl = document.getElementById("consoleEl");

function topnav(event) {
	
	// Turn all panels off

	var node = event.target.getAttributeNode("link");
	
	// Only turn on the panel that was selected
	
	if (node != null) {
		var link = node.value;
		el = document.getElementById(link)
		viewPanel(el)
	}
}

function viewPanel(element) {
	
	// Turn off all the panels
	hidePanel(adminEl)
	hidePanel(infrastructureEl)
	hidePanel(dataEl)
	hidePanel(consoleEl)
	
	if (element != null) {
		element.style.opacity = 1;
		element.style.zIndex = "1";
		element.addEventListener('click', pageMenu, false)
	} else {
		consAppend("viewPanel - elementn is null")
	}
}

function hidePanel(element) {

	if (element.style.opacity == 1) {
		element.removeEventListener('click', pageMenu, false)
	} 
	element.style.opacity = 0;
	element.style.zIndex = "-1";
}

//-------- Menu Page -----------

function pageMenu(event) {
	el = event.target;
	var node = event.target.getAttributeNode("link");
	consAppend('    .node:'+ node);
		
	if (node != null) {
		var link = node.value;
		consAppend(' Link:' + link);
		if (link == 'browse') {
			browse();
		}
	} else {
		consAppend('You pressed a null node')
	}
}

function consAppendtxt(event) {
	var msg = 'Just some some text<br>More Text<br>'
	consAppend(msg)
}

//-------- Menue level Functions -----------

function browse() {
	consAppend('Ok now we are in teh browse function here we go....');
	talkToServerHtml('/data/',null,browseResponse,null);
}

function browseResponse(data,event) {
	consAppend('Ok so now here is our response from browse:...');
	el = document.getElementById('data');
    el.innerHTML = data;
	
}

//-------- Common Functions -----------

function consAppend(msg) {
	el = document.getElementById('consoleEl')
    el.innerHTML = el.innerHTML + msg +'<br>'
}

function consClear() {
	el = document.getElementById('consoleEl')
    el.innerHTML = ""
}

function talkToServerHtml(location,data,functionToExecute,event) {
    
    xhr = new XMLHttpRequest();
    xhr.open('POST',location,true);
    xhr.setRequestHeader("Content-type", "application/html");
    xhr.onload = function() {
        if (xhr.status == 200) {
//            consAppend(xhr.responseText);
            data = xhr.responseText;
            functionToExecute(data,event);
        } else {
        	functionToExecute(data);
        	consAppend('*** We have a bad response from server: ' + xhr.status)
            consAppend('    url: ' + location)
            consAppend('    data: ' + data)
        }
    }
    xhr.send();
}


//-------- Listeners -----------

document.getElementById('topnavID').addEventListener('click', topnav, false)
document.getElementById('topnavID').addEventListener('mouseover', topnav, false)
document.getElementById('clear').addEventListener('click', consClear, false)
document.getElementById('consAppend').addEventListener('click', consAppendtxt, false)

