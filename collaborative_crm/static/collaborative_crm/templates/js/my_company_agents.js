//Datatable
$('#users-table').DataTable({
    language: {
        lengthMenu: 'Mostrar _MENU_ filas por pagina',
        zeroRecords: 'No hay resultados',
        info: '',
        infoEmpty: 'No hay registros disponibles',
        infoFiltered: '(filtros aplicados a un total de _MAX_ filas)',
        sInfoThousands: ".",
        sSearch: 'Filtrar '

    },
    columns: [
        {width: "30%", orderable: true},
        {width: "25%", orderable: true},
        {width: "25%", orderable: true},
        {width: "12%", orderable: false}
    ],
    order: [[0, 'asc']],
    responsive: true,
    bFilter: true,
    oPaginate: false,
    paging: false,
    searching: true
})
//Datatable

//Username logic
var checkUsernameExistence = function(value, $elem) {
    if (value) {
        $.ajax({
            url: '/usuarios_existentes',
            method: 'GET',
            dataType: 'json',
            success: function(r) {
                if (r.indexOf(value) > -1) {
                    $elem.parent().addClass('has-error')
                    $('#save-user').prop('disabled', true)
                    $('#existing-username').show()
                } else {
                    $elem.parent().removeClass('has-error')
                    $('#save-user').prop('disabled', false)
                    $('#existing-username').hide()
                }
            }
        })
    } else {

    }
}

$('input#email').change(function() {
    var thisElem = this
    $(thisElem).val($(thisElem).val().trim())
    checkUsernameExistence($(thisElem).val(), $(thisElem))
})
//Username logic

//Add/Edit user logic
var loadUserForm = function(data) {
    $('form#user-info').attr('user-id', data.id ? data.id : '0').attr('action', '/crm/empresa/' + $('form#user-info').attr('company-id') + '/usuarios/' + (data.id ? data.id : '0') + '/actualizar_datos')
    $('#user-box-title').text(data.full_name ? data.full_name : 'Nuevo Usuario')
    $('input#email').val(data.username ? data.username : '')
    $('input#first-name').val(data.first_name ? data.first_name : '')
    $('input#last-name').val(data.last_name ? data.last_name : '')
    $('input#telephone-number').val(data.telephone_number ? data.telephone_number : '')
    $('select#type').val(data.first_group_id ? data.first_group_id : '3').trigger('change')
    $('select#main-branch').val(data.main_branch_id ? data.main_branch_id : '0')
    $('select#users-in-charge').val(data.is_super_agent ? data.users_in_charge_ids : []).trigger('change')
    if (data.is_super_agent) {
        $('div.users-in-charge-row').show()
        $('select#users-in-charge option').prop('disabled', false)
        $('select#users-in-charge option[value=' + $('form#user-info').attr('user-id') + ']').prop('disabled', true)
        $('select#users-in-charge').select2({language: {'noResults': function() {return 'No hay datos'}}})
        $('.select2-container').css('width', '100%')
    } else {
        $('div.users-in-charge-row').hide()
    }
    $('input#add-new-users-to-my-charge').prop('checked', data.add_new_users_to_my_charge ? data.add_new_users_to_my_charge : false)
    $('input#add-my-branch-users-to-my-charge').prop('checked', data.add_my_branch_users_to_my_charge ? data.add_my_branch_users_to_my_charge : false)
    $('select#users-in-charge option').prop('disabled', false)
    $('.content-wrapper').animate({scrollTop: $('.user-form-row').position().top})
}
$('select#type').change(function() {
    if ($('select#type option:selected').attr('super-agent') == 'yes') {
        $('.select2-container').css('width', '100%')
        $('div.users-in-charge-row').show()
    } else {
        $('div.users-in-charge-row').hide()
    }
})

$('#scroll-to-zero').click(function() {$('.content-wrapper').animate({scrollTop: 0})})

$('#add-user').click(function() {loadUserForm({})})

$('.edit-user').click(function() {
    $tr = $(this).parents('tr.user-row')
    userId = parseInt($tr.attr('id'))
    $.ajax({
        url: '/crm/empresa/' + $('form#user-info').attr('company-id') + '/usuarios/' + userId + '/detalles',
        method: 'GET',
        data: 'json',
        success: function(r) {
            loadUserForm(r)
        }
    })
})
//Add/Edit user logic

//Password reset logic
$('.reset-password').click(function() {
    var $tr = $(this).parents('tr.user-row')
    $('#reset-password-modal b#reset-password-user-name').text($tr.find('td.name').text())
    $('#reset-password-modal').attr('user-id', $tr.attr('id')).modal('show')
})

$('button#confirm-reset-password').click(function() {
    $.ajax({
        url: '/crm/empresa/' + $('form#user-info').attr('company-id') + '/usuarios/' + $('#reset-password-modal').attr('user-id') + '/password_reset',
        method: 'POST',
        dataType: 'json',
        success: function(r) {
            if (r.status == 'Ok') {
                $('#reset-password-modal button#confirm-reset-password').hide()
                $('#reset-password-modal button#cancel-back-button').text('Volver')
                $('#reset-password-modal b#new-password').text('Nuevo password: ' + r.new_password)
            } else {
                alert(r.exception_class + ' - ' + r.exception_message)
            }
        }
    })
})

$('#reset-password-modal').on('shown.bs.modal', function() {
    $('#reset-password-modal button#confirm-reset-password').show()
    $('#reset-password-modal button#cancel-back-button').text('Cancelar')
    $('#reset-password-modal b#new-password').text('')
})
//Password reset logic

//Users in charge logic
$('select#users-in-charge').select2({language: {'noResults': function() {return 'No hay datos'}}})

$('button#users-in-charge-add-all').click(function() {
    userIds = $.map($('select#users-in-charge option'), function(e) {return $(e).val()}).filter(function(e) {return e != $('form#user-info').attr('user-id')})
    $('select#users-in-charge').val(userIds).trigger('change')
})
$('button#users-in-charge-add-all-branch').click(function() {
    currentValues = $('select#users-in-charge').val() ? $('select#users-in-charge').val() : []
    userIds = currentValues.concat($.map(parseInt($('select#main-branch').val()) ? $('select#users-in-charge option[branch-id=' + $('select#main-branch').val() + ']') : [], function(e) {return $(e).val()}).filter(function(e) {return e != $('form#user-info').attr('user-id')}))
    $('select#users-in-charge').val(userIds).trigger('change')
})
$('button#users-in-charge-remove-all').click(function() {$('select#users-in-charge').val([]).trigger('change')})
//Users in charge logic

//Remove logic
$('.remove-user').click(function() {
    var $tr = $(this).parents('tr.user-row')
    $('#remove-user-modal b#remove-user-name').text($tr.find('td.name').text())
    $('#remove-user-modal').attr('user-id', $tr.attr('id')).modal('show')
})

$('button#confirm-remove').click(function() {
    $.ajax({
        url: '/crm/empresa/' + $('form#user-info').attr('company-id') + '/usuarios/' + $('#remove-user-modal').attr('user-id') + '/eliminar',
        method: 'DELETE',
        dataType: 'json',
        success: function(r) {
            if (r.status == 'Ok') {
                window.location.href = r.redirect
            } else {
                alert(r.exception_class + ' - ' + r.exception_message)
            }
        }
    })
})
//Remove logic