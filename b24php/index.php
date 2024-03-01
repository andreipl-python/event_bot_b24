<body>
<link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css"
	  crossorigin="anonymous">
<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.3.1/jquery.min.js"></script>
<div class="container-fluid">
	<div class=" m-5">
		<div id="chat_history" class="row">
			<div class="spinner-border m-5 text-success" role="status">
				<span class="sr-only">Loading...</span>
			</div>
		</div>
		<div id="chat_form" class=" mt-5 mr-auto ml-auto mb-5">
			<form id="form_message">
				<div class="form-group">
					<label for="name">Name</label>
					<input type="text" class="form-control" placeholder="Name">
				</div>
				<div class="form-group">
					<label for="message">Message</label>
					<textarea class="form-control" name="message" rows="3" placeholder="your message here"></textarea>
				</div>
				<input class="btn btn-primary" type="submit" name="send" value="send">
			</form>
		</div>
	</div>
</div>
<script>
	$(document).ready(function () {
		function updateChat()
		{
			$.ajax({
				'method': 'POST',
				'dataType': 'html',
				'url': 'ajax.php',
				'data': 'type=chat_history',
				success: function (data) {
					$('#chat_history').text('').html(data);
				}
			});
		}
		setInterval(updateChat, 5000);
		updateChat();
		$('#form_message').on('submit', function (el) {
			el.preventDefault();
			$('#chat_form').addClass('spinner-border');
			$('#form_message').hide();
			var formData = $(this).serialize();
			$.ajax({
				'method': 'POST',
				'dataType': 'json',
				'url': 'ajax.php',
				'data': formData + '&type=send_message',
				success: function (data) {
					updateChat();
					$('#chat_form').removeClass('spinner-border');
					$('#form_message textarea[name=message]').val('');
					$('#form_message').show();
				}
			});
		});
	});
</script>
</body>

