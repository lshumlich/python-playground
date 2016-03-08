
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
	} else {
		consAppend('You pressed a null node')
	}
}

function consAppendtxt(event) {
	var msg = 'Just some some text<br>More Text<br>'
	consAppend(msg)
	
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

//-------- Listeners -----------

document.getElementById('topnavID').addEventListener('click', topnav, false)
document.getElementById('topnavID').addEventListener('mouseover', topnav, false)
document.getElementById('clear').addEventListener('click', consClear, false)
document.getElementById('consAppend').addEventListener('click', consAppendtxt, false)

