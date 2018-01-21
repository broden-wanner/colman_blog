//Adds boop message upon loading the page
$(function() {
	var $boopMessage = $('<p>Boop</p>').css('display', 'none').addClass('boop-message').addClass('noselect');
	$boopMessage.appendTo('body');
	$boopMessage.delay(3000).slideDown(1000).delay(1000).fadeOut(2000);
});

