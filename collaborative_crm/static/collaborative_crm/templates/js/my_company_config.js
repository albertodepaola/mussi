//Company logo upload
$(function() {
    Dropzone.options.uploadCompanyLogo = {
            acceptedFiles: 'image/*',
            success: function(file, response){
                if (response.status == 'Ok') {
                    window.location.reload()
                } else {
                    alert('Error inesperado: ' + response.error_message)
                }
            }
        }
    }
)
//Company logo upload

//Permissions logic
$('input#edit-config').change(function() {
    if ($('input#edit-config').prop('checked')) {
        $('input#config-notifications').prop('disabled', false)
    } else {
        $('input#config-notifications').prop('checked', false)
        $('input#config-notifications').prop('disabled', true)
    }
})
//Permissions logic

//Group notifications config logic
$('select#user-type').change(function() {
    var thisElem = this
    groupId = parseInt($(thisElem).val())
    $('form#notifications').attr('action', '/crm/mi_empresa/grupo/' + groupId + '/actualizar_configuracion_notificaciones')
    if (groupId) {
        $.ajax({
            url: '/crm/mi_empresa/grupo/' + groupId + '/configuracion_notificaciones',
            method: 'GET',
            dataType: 'json',
            success: function(r) {
                if (r.status == 'Ok') {
                    $.each(r.configs, function(k, e) {
                        $('.row[notification-type=' + e.type_id + '] .notify').prop('checked', e.notify)
                        $('.row[notification-type=' + e.type_id + '] .email').prop('checked', e.email)
                        editView = e.can_edit ? 'can_edit' : (e.can_view ? 'can_view' : 'none')
                        $('.row[notification-type=' + e.type_id + '] .edit-view[value=' + editView + ']').prop('checked', true)
                        $('.edit-view').prop('disabled', $(thisElem).find('option:selected').attr('is-admin') == 'yes')
                    })
                    $('div#config, .group-config-alert, button#save-config').show()
                } else {
                    alert(r.exception_class + ' - ' + r.exception_message)
                }
            }
        })
    } else {
        $('div#config, .group-config-alert, button#save-config').hide()
    }
})

$('select#user-type').trigger('change')
//Group notifications config logic

//Workflow
$('select#workflow').change(function() {
    var workflowId = parseInt($(this).val())
    if (!workflowId) {
        $('input#workflow-name').parent().show()
        $('input#workflow-active').prop('checked', false)
        $('textarea#workflow-description').val(null)
        $('a#remove-workflow').hide()
        workflowCanvasObject.clearAll(true)
    } else {
        $('input#workflow-name').parent().hide()

        if ($('select#workflow option:selected').attr('is-default') == 'yes') {
            $('a#remove-workflow').hide()
        } else {
            $('a#remove-workflow').show()
        }

        $.ajax({
            url: '/crm/workflows/' + workflowId + '/detalles',
            method: 'GET',
            dataType: 'json',
            success: function(r) {
                $('input#workflow-active').prop('checked', r.isActive)
                $('textarea#workflow-description').val(r.description)
                workflowCanvasObject.loadJson(r, true)
            }
        })
    }
})

$('select#workflow').trigger('change')
var workflowCanvasObject = new wc.WorkflowCanvas($('div#canvas-container'), $('.content-wrapper'))

var workflowSaveError = function(action, msg) {
    $('#error-saving-workflow-modal text.action').text(action)
    $('#error-saving-workflow-modal p#error-saving-workflow-message').text(msg)
    $('#error-saving-workflow-modal').modal('show')
}

$('button#save-workflow').click(function() {
    if (workflowCanvasObject.hasIsolatedStates()) {
        workflowSaveError('guardar', 'El workflow tiene estados aislados (bordes rojos). Todos los estados deben estar comunicados con al menos otro estado a través de, al menos, una acción.')
        return false
    }
    if (workflowCanvasObject.hasNoInitialState()) {
        workflowSaveError('guardar', 'El workflow no tiene estado inicial (bordes verdes). Debe ser un estado sin ninguna acción que dirija a el.')
        return false
    }
    if (workflowCanvasObject.hasManyInitialStates()) {
        workflowSaveError('guardar', 'El workflow tiene más de un estado inicial (bordes verdes). Sólo puede haber uno.')
        return false
    }
    $.ajax({
        url: '/crm/mi_empresa/guardar_workflow',
        method: 'POST',
        data: workflowCanvasObject.toJson({
            id: parseInt($('select#workflow').val()),
            name: parseInt($('select#workflow').val()) ? $('select#workflow option:selected').text().trim() : $('input#workflow-name').val(),
            description: $('textarea#workflow-description').val(),
            isActive: $('input#workflow-active').prop('checked')
        }),
        dataType: 'json',
        success: function(r) {
            if (r.status == 'Ok') {
                window.location.reload()
            } else {
                workflowSaveError('guardar', r.error_message)
            }
        }
    })
})

$('a#remove-workflow').click(function() {
    $('#confirm-delete-workflow-modal').modal('show')
})

$('button#remove-workflow').click(function() {
    $.ajax({
        url: '/crm/workflows/' + parseInt($('select#workflow').val()) + '/eliminar',
        method: 'DELETE',
        dataType: 'json',
        success: function(r) {
            if (r.status == 'Ok') {
                window.location.reload()
            } else {
                workflowSaveError('eliminar', r.exception_class + ' - ' + r.exception_message)
            }
        }
    })
})
//Workflow
