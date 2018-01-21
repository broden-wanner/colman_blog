



//Like button function functionality
$('#like-button').on('submit', function(e) {
	e.preventDefault();
	$.ajax({
		url: $(this).attr('action'),
		method: $(this).attr('method')
	});
	console.log('did something')
});

console.log('this works')