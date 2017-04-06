var evtSrc = new EventSource("/subscribe");

function turnLightOn(device){
	if (device.indexOf('_b') > -1){
		turnOnYellow(device);
	} else if (device.indexOf('_s') > -1){
		turnOnRed(device);
	} else if (device.indexOf('_c') > -1){
		turnOnGreen(device);
	} else {
		turnOnBlue(device);
	}
}

evtSrc.onmessage = function(e) {
	var obj = JSON.parse(e.data);
	var device = $('#'+obj.device).get(0);
	if (typeof device == 'undefined'){
		return;
	}
	switch (device.getAttribute('data-type')){
		case 'light':
			if (obj.resource == 15011){
				if (obj.value == 0)
					turnOff(obj.device);
				else
					turnLightOn(obj.device);
			} else {
				updateText(obj.device, obj.value.toString()+" %");
			}
			break;

		case 'illuminance':
			turnOnGreen(obj.device);
			updateText(obj.device, obj.value.toString()+" lx");
			break;

		case 'motion':
			if (obj.value == 0)
				turnOff(obj.device);
			else
				turnOnRed(obj.device);
			break;

		case 'ac':
			if (obj.value == 0)
				device.firstChild.data = "OFF";
			else
				device.firstChild.data = "ON";
			break;

		case 'humidity':
			device.firstChild.data = obj.value.toString()+" %";
			break;

		case 'temperature':
			device.firstChild.data = obj.value.toString()+"°C";
			break;
	}
 };