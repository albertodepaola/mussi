//Set the CSRF header for all ajax (HTTP_X_CSRFTOKEN)
$(function () {
    $.ajaxSetup({
        headers: { 'X-CSRFToken': $.cookie('csrftoken') }
    })
})
//Set the CSRF header for all ajax (HTTP_X_CSRFTOKEN)

var resetPasswordEmail = function() {
    $('#login-error').remove()
    $('#reset-password-email').remove()
    $('#new-line').remove()
    $('#new-password-sent').remove()
    $.ajax({
        url: '/reset_password_email',
        method: 'POST',
        data: $('#inputUserName').val(),
        success: function() {
            $('#inputPassword').after($('<span/>', {id: 'new-password-sent', class: 'label label-success', text: 'Nuevo password enviado'}))
            setTimeout(function() {$('#new-password-sent').remove()}, 3000)
        }
    })
}

$('div.content-wrapper, footer.main-footer').css('margin-left', '0px')

var tryLogIn = function() {
	$.ajax(
		{
			url: '/login_usuario',
			method: 'POST',
			dataType: 'json',
			data: JSON.stringify({username: $('#inputUserName').val() ? $('#inputUserName').val() : '', password: $('#inputPassword').val() ? $('#inputPassword').val() : ''}),
			success: function(data){
				if (data.status == 'Error') {
                    $('#inputPassword').val('')
					$('#login-error').remove()
					$('#reset-password-email').remove()
					$('#new-password-sent').remove()
					$('#new-line').remove()
					$('#inputPassword').after($('<span/>', {id: 'login-error', class: 'label label-danger', text: data.error_message}))
                    if (data.error_message == 'Usuario inexistente' || data.error_message == 'Usuario bloqueado, contáctenos para debloquearlo') {
                        $('#inputUserName').focus()
                    } else {
                        $('#inputPassword').focus()
                        $('#login-error').after($('<span/>', {id: 'reset-password-email', class: 'label label-warning', text: 'Enviarme nuevo password por email'}).click(resetPasswordEmail)).after($('<b/>', {id: 'new-line'}).append('<br>'))
                    }
				} else {
					window.location.href = data.redirect
				}
			}
		}
	)
}

$('#inputUserName').keypress(function(e) {
		if (e.keyCode == 13 && ($('#inputUserName').val() ? $('#inputUserName').val() : '') != '') {
			$('#inputPassword').focus()
		}
	}
)

$('#inputPassword').keypress(function(e) {
		if (e.keyCode == 13 && ($('#inputPassword').val() ? $('#inputPassword').val() : '') != '') {
			tryLogIn()
		}
	}
)

$('button').click(tryLogIn)
$('#inputUserName').focus()