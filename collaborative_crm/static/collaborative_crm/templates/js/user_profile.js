//Change password
password = document.getElementById('new-password')
repeatPassword = document.getElementById('new-password-repeat')

var validatePassword = function () {
    if (password.value != repeatPassword.value) {
        repeatPassword.setCustomValidity('No coincide')
    } else {
        repeatPassword.setCustomValidity('')
    }
}

$(password).change(validatePassword)
$(repeatPassword).keyup(validatePassword)
//Change password

//Tones
$('select#notifications-tone, select#messages-tone').change(function() {
    playSound(parseInt($(this).val()))
})

$('.play-tone').click(function() {
    $(this).parents('.form-group').find('select').trigger('change')
})
//Tones