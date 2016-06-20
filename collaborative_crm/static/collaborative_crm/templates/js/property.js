//slimScroll set up
$(function(){
    $('.box-body.attributes, .box-body.interested-contacts, .box-body.multi-posting, .box-body.history').slimScroll({
        height: '250px'
    })
})
//slimScroll set up

//Select2 set up
$('select#type').select2({language: {'noResults': function() {return 'No hay datos'}}})
$('select#status').select2({language: {'noResults': function() {return 'No hay datos'}}})
//Select2 set up

//TouchSpin set up
$('input#sale-price').TouchSpin({
    min: 0,
    max: 1000000000,
    decimals: 0,
    step: 500,
    prefix: '$',
    postfix: '',
    boostat: 5,
    maxboostedstep: 10000,
    mousewheel: false
})

$('input#sale-price-usd').TouchSpin({
    min: 0,
    max: 1000000000,
    decimals: 0,
    step: 500,
    prefix: 'US$',
    postfix: '',
    boostat: 5,
    maxboostedstep: 10000,
    mousewheel: false
})

$('input#rent-price').TouchSpin({
    min: 0,
    max: 1000000000,
    decimals: 0,
    step: 50,
    prefix: '$',
    postfix: '',
    boostat: 5,
    maxboostedstep: 1000,
    mousewheel: false
})

$('input#rent-price-usd').TouchSpin({
    min: 0,
    max: 1000000000,
    decimals: 0,
    step: 5,
    prefix: 'US$',
    postfix: '',
    boostat: 5,
    maxboostedstep: 100,
    mousewheel: false
})

var enableDisableTouchSpin = function($elem, enabled) {
    $elem.prop('disabled', !enabled || $elem.hasClass('blocked'))
    $elem.parent().find('span.input-group-btn button').prop('disabled', !enabled || $elem.hasClass('blocked'))
}

$('input#for-sale').change(function() {enableDisableTouchSpin($('input#sale-price, input#sale-price-usd'), $('input#for-sale').prop('checked'))})
$('input#for-rent').change(function() {enableDisableTouchSpin($('input#rent-price, input#rent-price-usd'), $('input#for-rent').prop('checked'))})

$('input#for-sale, input#for-rent').trigger('change')
//TouchSpin set up

//Status-appraisal logic
var saleRentStatusChanged = function() {
    if ((!$('input#sale-price').val() || $('input#sale-price').val() == 0) && (!$('input#sale-price-usd').val() || $('input#sale-price-usd').val() == 0) && (!$('input#rent-price').val() || $('input#rent-price').val() == 0) && (!$('input#rent-price-usd').val() || $('input#rent-price-usd').val() == 0)) {
        appraisalPendingValue = $('select#status option').filter(function(k, o) {return $(o).text() == 'Pendiente de tasación'}).attr('value')
        $('select#status').val(appraisalPendingValue).trigger('change').prop('disabled', true)
    } else {
        if (!$('input#for-sale').prop('checked') && !$('input#for-rent').prop('checked')) {
            unavailableValue = $('select#status option').filter(function(k, o) {return $(o).text() == 'No disponible'}).attr('value')
            $('select#status').val(unavailableValue).trigger('change').prop('disabled', true)
        } else {
            availableValue = $('select#status option').filter(function(k, o) {return $(o).text() == 'Disponible'}).attr('value')
            $('select#status').val(availableValue).trigger('change').prop('disabled', false)
        }
    }
}

//$('input#for-sale, input#for-rent, input#sale-price, input#sale-price-usd, input#rent-price, input#rent-price-usd').change(saleRentStatusChanged)
//Status-appraisal logic

//edit on change/create property logic
var showMandatoryToolTip = function(e) {
    if (!$(e).val() || $(e).val() == '') {
        var $elem = !$(e).hasClass('edit-on-change-select') ? $(e) : $(e).parent().find('span.select2-container')
        if (!$elem.hasClass('tooltipstered')) {
            $elem.tooltipster({
                trigger: 'custom',
                position: 'top',
                theme: 'tooltipster-validation'
            })
        }
        $elem.tooltipster('update', 'Calle, Número y Ciudad deben informarse antes de guardar')
        $elem.tooltipster('show')
        $elem.unbind('focusin').focusin(function() {
            thisElem = this
            $(thisElem).tooltipster('hide')
            $(thisElem).unbind('focusin').unbind('click')
        })
    }
}

var saveProperty = function() {
    if ($('.mandatory').filter(function(k, e) {return !$(e).val() || ['', '0', '-1'].indexOf($(e).val()) > -1}).length > 0) {
        $.each($('.mandatory'), function(k, e) {showMandatoryToolTip(e)})
    } else {
        if ($('a#new-property-owner').attr('contact-id')) {$('form#property-basic-info').append($('<input/>', {type: 'hidden', name: 'owner-id'}).val($('a#new-property-owner').attr('contact-id')))}
        if ($('a#new-property-interested-contact').attr('contact-id')) {$('form#property-basic-info').append($('<input/>', {type: 'hidden', name: 'interested-contact-id'}).val($('a#new-property-interested-contact').attr('contact-id')))}
        $('#created-property-modal').modal('show')
        setTimeout(function() {
            $('form#property-basic-info').submit()
        }, 2500)
    }
}

var setUpEditOnChangeLogic = function() {
    if ($('form#property-basic-info').attr('property-id') != '0') {
        editOnChangeControlsCurrentValues = $.map($('.edit-on-change, .edit-on-change-checkbox, .edit-on-change-select'), function(c) {return {control: $(c).attr('id'), currentValue: $(c).hasClass('edit-on-change') ? $(c).val() : $(c).prop('checked')}})

        var save = function(thisElem, saveBlank, touchSpinForm, checkbox) {
            var $groupFormElem = (!touchSpinForm && !checkbox) ? $(thisElem).parent() : $(thisElem).parent().parent()
            var newValue = ($(thisElem).hasClass('edit-on-change') || $(thisElem).hasClass('edit-on-change-select')) ? $(thisElem).val() : $(thisElem).prop('checked')
            if ((((newValue && newValue != '') || checkbox) || saveBlank) && newValue != editOnChangeControlsCurrentValues.filter(function(v) {return v.control == $(thisElem).attr('id')})[0].currentValue) {
                $groupFormElem.removeClass('has-warning')
                if (saveBlank && (!newValue || newValue == '') && $(thisElem).hasClass('mandatory')) {
                    showMandatoryToolTip(thisElem)
                } else {
                    $.ajax({
                        url: '/crm/propiedad/' + $('form#property-basic-info').attr('property-id') + '/actualizar_campo',
                        method: 'POST',
                        data: JSON.stringify({fieldName: $(thisElem).attr('id'), fieldValue: newValue}),
                        dataType: 'json',
                        success: function(r) {
                            if (r.status == 'Ok') {
                                if (r.change) {
                                    $groupFormElem.addClass('has-success')
                                    editOnChangeControlsCurrentValues.filter(function(v) {return v.control == $(thisElem).attr('id')})[0].currentValue = newValue
                                    setTimeout(function() {
                                        $groupFormElem.removeClass('has-success')
                                    }, 4000)
                                    //Update anonymous address when street and/or number are changed, if applies
                                    if (['street', 'number'].indexOf($(thisElem).attr('id')) > -1 && r.new_anonymous_address && r.new_anonymous_address != '' && r.new_anonymous_address != $('input#anonymous-address').val()) {
                                        $('input#anonymous-address').val(r.new_anonymous_address).trigger('focusout')
                                    }
                                    //Update anonymous address when street and/or number are changed, if applies

                                    //Update status when sale/rent fields force a change in property's status
                                    if ($(thisElem).hasClass('forces-status')) {saleRentStatusChanged()}
                                    //Update status when sale/rent fields force a change in property's status
                                }
                            } else {
                                $groupFormElem.addClass('has-error')
                            }
                        }
                    })
                }
            }
        }

        var editOnChangeKeyUp = function(e, thisElem, touchSpinForm) {
            if ([9, 13, 27].indexOf(e.keyCode) == -1) {
                var $groupFormElem = !touchSpinForm ? $(thisElem).parent() : $(thisElem).parent().parent()
                if ($(thisElem).val() != editOnChangeControlsCurrentValues.filter(function(v) {return v.control == $(thisElem).attr('id')})[0].currentValue) {
                    $groupFormElem.removeClass('has-success')
                    $groupFormElem.removeClass('has-error')
                    $groupFormElem.addClass('has-warning')
                } else {
                    $groupFormElem.removeClass('has-warning')
                }
            } else {
                if (e.keyCode == 13 && !touchSpinForm) {
                    save(thisElem, true)
                }
            }
        }

        $('.edit-on-change').keyup(function(e) {thisElem = this; editOnChangeKeyUp(e, thisElem, $(thisElem).hasClass('touch-spin'), $(thisElem).hasClass('edit-on-change-checkbox'))})
        $('.edit-on-change').focusout(function() {thisElem = this; save(thisElem, false, $(thisElem).hasClass('touch-spin'), $(thisElem).hasClass('edit-on-change-checkbox'))})
        var onChangeFunction = function() {
            thisElem = this
            if (!$(thisElem).is(':focus') || !$(thisElem).hasClass('touch-spin')) {save(thisElem, false, $(thisElem).hasClass('touch-spin'), $(thisElem).hasClass('edit-on-change-checkbox'))
        }}
        $('.edit-on-change-checkbox, .edit-on-change-select').change(onChangeFunction)
        $('.edit-on-change.touch-spin').change($.throttle(2000, onChangeFunction))
    } else {
        $('.edit-on-change').focusout(saveProperty)
        $('.edit-on-change-checkbox, .edit-on-change-select').change(saveProperty)
        $('.edit-on-change.touch-spin').change($.throttle(2000, saveProperty))
    }
}
//edit on change/create property logic

//geography hierarchy logic
setUpGeographyHierarchies('property', true, setUpEditOnChangeLogic)
//geography hierarchy logic

//History logic
setUpHistoryLogic($('a.name.history'), 'propiedad', $('form#property-basic-info').attr('property-id'))
//History logic

//Owner/Interested Contacts logic
var unbindContactFromProperty = function() {
    var contactId = $(this).attr('contact-id')
    var propertyId = $(this).attr('property-id')
    $.ajax({
        url: '/crm/contacto/' + contactId + '/propiedad/' + propertyId + '/desvincular',
        method: 'DELETE',
        dataType: 'json',
        success: function(r) {
            if (r.status == 'Ok') {
                $('a.interested-contact[contact-id=' + contactId + ']').parents('div.item').remove()
            } else {
                alert(r.exception_class + ' - ' + r.exception_message)
            }
        }
    })
}

var contactPropertyRelationshipCommentary
$('a#owner, a.interested-contact').click(function() {
    thisElem = this
    showContactDetailsModal($(thisElem).attr('contact-id'), $('form#property-basic-info').attr('property-id'), unbindContactFromProperty)
})
//Owner/Interested Contacts logic

//Assign Owner/Agent logic
//Assign owner logic
$('#assign-owner').click(function() {
    $('div#owner-search').show()
    $('#assign-owner-search').focus()
})

$('i#cancel-assign-owner').click(function() {
    $('#assign-owner-search').val('').trigger('change')
    $('div#owner-search').hide()
    $('div#owner-search-results').empty()
})

var assignAsOwner = function() {
    contactId = $(this).attr('contact-id')
    $.ajax({
        url: '/crm/contacto/' + contactId + '/propiedad/' + $('form#property-basic-info').attr('property-id') + '/vincular/dueno',
        method: 'POST',
        dataType: 'json',
        success: function(r) {
            if (r.status == 'Ok') {
                window.location.reload()
            } else {
                alert(r.exception_class + ' - ' + r.exception_message)
            }
        }
    })
}

$('#assign-owner-search').keyup($.throttle(750, function(e) {assignContactsAgentsSearch(e, this, 'owner', 'contactos', $('div#owner-search-results'), assignAsOwner, 'contact-id')})).keydown(function(e) {if (e.which === 27) {$('div#owner-search-results').empty()}; searchKeyDown(e, this, '.assign-owner-search-item', $('input#assign-owner-search'))})

$('a#unbind-owner').click(function() {
    var thisElem = this
    $.ajax({
        url: '/crm/contacto/' + $(thisElem).attr('contact-id') + '/propiedad/' + $('form#property-basic-info').attr('property-id') + '/desvincular',
        method: 'DELETE',
        dataType: 'json',
        success: function(r) {
            if (r.status == 'Ok') {
                window.location.reload()
            } else {
                alert(r.exception_class + ' - ' + r.exception_message)
            }
        }
    })
})
//Assign owner logic

//Assign agent logic
var assignAgentToProperty = function() {
    assignAgent($('form#property-basic-info').attr('property-id'), $(this).attr('user-id'), 'propiedad')
}

$('#assign-me-agent').click(assignAgentToProperty)
$('#assign-agent-search').keyup($.throttle(750, function(e) {assignContactsAgentsSearch(e, this, 'agent', 'agentes-a-cargo', $('div#agent-search-results'), assignAgentToProperty, 'user-id')})).keydown(function(e) {if (e.which === 27) {$('div#agent-search-results').empty()}; searchKeyDown(e, this, '.assign-agent-search-item', $('input#assign-agent-search'))})

var unassignAgentToProperty = function() {assignAgent($('form#property-basic-info').attr('property-id'), undefined, 'propiedad')}
$('a#unbind-agent').click(unassignAgentToProperty)
//Assign agent logic
//Assign Owner/Agent logic

//Extra attribute logic
var initializeDataTable = function() {
    $('#edit-attributes-modal .modal-body').scrollTop(0)

    if (!$('#extra-attributes-table').hasClass('dataTable')) {
        $('#extra-attributes-table').DataTable({
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
                {width: "25%", orderable: true},
                {width: "15%", orderable: true},
                {width: "15%", orderable: false},
                {width: "10%", orderable: false},
                {width: "15%", orderable: false},
                {width: "15%", orderable: false},
                {width: "5%", orderable: false}
            ],
            order: [[1, 'desc']],
            responsive: true,
            bFilter: false,
            oPaginate: false,
            paging: false,
            searching: false
        })
    }
}

var enableUnitBeforeCheckbox = function() {
    thisElem = this
    $unitBefore = $(thisElem).parents('tr').find('input#unit-before')
    if ($(thisElem).val()) {
        $unitBefore.prop('disabled', false)
    } else {
        $unitBefore.prop('disabled', true)
    }
}

var toggleNumericInput = function() {
    thisElem = this
    $value = $(thisElem).parents('tr').find('input#value')
    currentValue = $value.val()
    if ($(thisElem).prop('checked')) {
        setTouchSpin($value)
    } else {
        $value.parents('.bootstrap-touchspin').before($('<input/>', {class: 'text', type: 'text', maxlength: '200', id: 'value', value: currentValue})).remove()
    }
}

var removeAttribute = function() {
    thisElem = this
    var $tr = $(thisElem).parent().parent()
    if ($tr.hasClass('common')) {
        $tr.find('input#value').val(undefined).trigger('change')
    } else {
        $.ajax({
            url: '/crm/propiedad/' + $('form#property-basic-info').attr('property-id') + '/eliminar_atributo',
            method: 'DELETE',
            dataType: 'json',
            data: $tr.attr('id'),
            success: function () {
                $('#extra-attributes-table').DataTable().row($tr).remove().draw()
                $tr.remove()
            }
        })
    }
}

var setTouchSpin = function(elem) {
    $(elem).TouchSpin({
        verticalbuttons: true,
        min: 0,
        max: 1000000000,
        decimals: 0,
        step: 1,
        boostat: 5,
        maxboostedstep: 10000,
        mousewheel: false
    })
}

$('#add-attribute').click(function() {
    $('#extra-attributes-table').DataTable().row.add([
        $('<input/>', {id: 'new-row-input', type: 'text'}).prop('outerHTML'),
        'Agregado',
        $('<input/>', {class: 'text', type: 'text', maxlength: '200', id: 'value'}).prop('outerHTML'),
        $('<input/>', {type: 'text', maxlength: '5', id: 'unit-value', class: 'unit-value'}).prop('outerHTML'),
        $('<div/>').append($('<label/>').append($('<input/>', {type: 'checkbox', id: 'numeric-attribute', class: 'numeric-attribute'})).append($('<b/>', {text: ' Numérico'}))).prop('outerHTML'),
        $('<div/>').append($('<label/>').append($('<input/>', {type: 'checkbox', id: 'unit-before', class: 'unit-before'})).append($('<b/>', {text: ' Unidad delante'}))).prop('outerHTML'),
        $('<a/>', {class: 'remove-attribute'}).append($('<i/>', {class: 'fa fa-trash'})).prop('outerHTML')
    ]).draw()

    $('input#new-row-input').focus()
    $('input#new-row-input').focusout(function() {
        var thisElem = this
        var $tr = $(thisElem).parent().parent()
        var attribute = $(thisElem).val()
        if (attribute) {
            $.ajax({
                url: '/crm/propiedad/' + $('form#property-basic-info').attr('property-id') + '/actualizar_atributo',
                method: 'POST',
                dataType: 'json',
                data: JSON.stringify({
                    attribute: attribute
                }),
                success: function(r) {
                    if (r.status == 'Ok') {
                        $tr.attr('id', attribute).addClass('custom')
                        $(thisElem).before(attribute).remove()
                        $tr.find('input').change(saveAttributeChange)
                        $tr.find('.remove-attribute').click(removeAttribute)
                        $tr.find('.unit-value').change(enableUnitBeforeCheckbox)
                        $tr.find('.numeric-attribute').change(toggleNumericInput)
                    } else {
                        alert(r.exception_class + ' - ' + r.exception_message)
                    }
                }
            })
        } else {
            $('#extra-attributes-table').DataTable().row($tr).remove().draw()
            $tr.remove()
        }
    })
})

$.each($('#edit-attributes-modal input.touchspin'), function(k, e) {setTouchSpin(e)})
$('.remove-attribute').click(removeAttribute)
$('tr.custom .unit-value').change(enableUnitBeforeCheckbox)
$('tr.custom .numeric-attribute').change(toggleNumericInput)

$('a#edit-attributes').click(function() {$('#edit-attributes-modal').modal('show')})
$('#edit-attributes-modal').on('shown.bs.modal', initializeDataTable)

var saveAttributeChange = function () {
    thisElem = this
    if ($(thisElem).attr('type') == 'text') {
        value = $(thisElem).val()
    } else {
        value = $(thisElem).attr('id') == 'numeric-attribute' ? ($(thisElem).prop('checked') ? 'Número' : '') : $(thisElem).prop('checked')
    }
    $.ajax({
        url: '/crm/propiedad/' + $('form#property-basic-info').attr('property-id') + '/actualizar_atributo',
        method: 'POST',
        dataType: 'json',
        data: JSON.stringify({
            attribute: $(thisElem).parents('tr').attr('id'),
            attribute_field: $(thisElem).attr('id'),
            value: value
        }),
        success: function(r) {
            if (r.status == 'Ok') {
                //do nothing
            } else {
                alert(r.exception_class + ' - ' + r.exception_message)
            }
        }
    })
}
$('#extra-attributes-table input').change(saveAttributeChange)

//Fix table header
//var initialPosition = $('#edit-attributes-modal thead').parent().parent().position().top
//$('#edit-attributes-modal .modal-body').scroll(function() {
//    if ($('#edit-attributes-modal .modal-body').scrollTop() > initialPosition) {
//        $('#edit-attributes-modal thead').parent().parent().position().top)
//    } else {
//
//    }
//})
//$('#edit-attributes-modal thead').position().top
//Fix table header

//Extra attribute logic

//Images logic
var showGallery = function(e) {
    e.preventDefault()
    $('#blueimp-gallery').data('useBootstrapModal', false).data('fullScreen', true)
    blueimp.Gallery($('#links a'), $('#blueimp-gallery').data())
}

var showPropertyImagesModal = function(e) {
    if ($('#images-modal').length > 0) {
        $('#images-modal').modal('show')
    } else {
        showGallery(e)
    }
}

$('#view-images').click(showPropertyImagesModal)
$('#property-cover-image').click(showPropertyImagesModal)

$(function () {
    'use strict'
    $('#blueimp-gallery').data('useBootstrapModal', false).data('fullScreen', true)
    $('#image-gallery-button').click(showGallery)
})

$(function() {
    Dropzone.options.uploadImages = {
            acceptedFiles: 'image/*',
            success: function(file, response){
                if (response.status == 'Ok') {
                    setTimeout(function() {window.location.href = response.redirect}, 2000)
                } else {
                    alert('Error inesperado: ' + response.error_message)
                }
            }
        }
    }
)

$('#image-description-modal').on('shown.bs.modal', function() {$('#image-description-modal textarea').focus()})

$('.edit-image-description').click(function() {
    var thisElem = this
    $('#image-description-modal').attr('img-id', $(thisElem).attr('img-id'))
    $('#image-description-modal textarea').val($(thisElem).parents('div.img-link').find('a').attr('title'))
    $('#image-description-modal').modal('show')
})

$('#save-image-description').click(function() {
    $.ajax({
        url: '/crm/propiedad/' + $('form#property-basic-info').attr('property-id') + '/imagenes/' + $('#image-description-modal').attr('img-id') + '/editar_descripcion',
        method: 'POST',
        dataType: 'json',
        data: $('#image-description-modal textarea').val(),
        success: function(r) {
            if (r.status == 'Ok') {
                $('div.img-link[img-id=' + $('#image-description-modal').attr('img-id') + '] a').attr('title', $('#image-description-modal textarea').val())
                $('#image-description-modal').modal('hide')
            } else {
                alert(r.exception_class + ' - ' + r.exception_message)
            }
        }
    })
})

$('.cover-image').change(function() {
    $.ajax({
        url: '/crm/propiedad/' + $('form#property-basic-info').attr('property-id') + '/imagenes/' + $('.cover-image:checked').val() + '/portada',
        method: 'POST',
        dataType: 'json',
        success: function(r) {
            if (r.status == 'Ok') {
                $('img#property-cover-image').attr('src', $('.cover-image:checked').parents('div.img-link').find('a').attr('href'))
            } else {
                alert(r.exception_class + ' - ' + r.exception_message)
            }
        }
    })
})

$('.remove-image').click(function() {
    var thisElem = this
    $.ajax({
        url: '/crm/propiedad/' + $('form#property-basic-info').attr('property-id') + '/imagenes/' + $(thisElem).attr('img-id') + '/eliminar',
        method: 'DELETE',
        dataType: 'json',
        success: function(r) {
            if (r.status == 'Ok') {
                $(thisElem).parents('div.img-link').remove()
            } else {
                alert(r.exception_class + ' - ' + r.exception_message)
            }
        }
    })
})
//Images logic

//Property excel/PDF file
$('button.property-file-button').click(function() {
    showFileModal($(this).attr('property-id'))
})
//Property excel/PDF file

//Remove logic
$('button#remove-property').click(function() {$('#remove-property-modal').modal('show')})
$('button#confirm-remove').click(function() {
    $.ajax({
        url: '/crm/propiedad/' + $('form#property-basic-info').attr('property-id') + '/eliminar',
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