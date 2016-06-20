//Set the CSRF header for all ajax (HTTP_X_CSRFTOKEN)
$(function () {
    $.ajaxSetup({
        headers: { 'X-CSRFToken': $.cookie('csrftoken') }
    })
})
//Set the CSRF header for all ajax (HTTP_X_CSRFTOKEN)

//Set my user id value
var myUserId = parseInt($('meta#user').attr('user-id'))
//Set my user id value

//Utils
String.prototype.replaceAll = function(search, replace)
{
    if (replace === undefined) {
        return this.toString()
    }
    return this.replace(new RegExp('[' + search + ']', 'g'), replace)
}

String.prototype.slugify = function()
{
    return this.toLowerCase().replace(/[^\w ]+/g,'').replace(/ +/g,'-')
}

String.prototype.toTitleCase = function()
{
    return this.replace(/\w\S*/g, function(txt){return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();});
}

Array.prototype.unique = function() {
    var a = this.concat()
    for(var i=0; i< a.length; ++i) {
        for(var j=i+1; j<a.length; ++j) {
            if(a[i] === a[j])
                a.splice(j--, 1)
        }
    }
    return a;
};
//Utils

//Geography hierarchies set up
var resetDropDown = function($elem, data, placeholder, setToZero) {
    $elem.empty()
    $elem.select2({
        data: data,
        placeholder: {
            id: '0',
            text: placeholder
          },
        allowClear: true,
        language: {
            'noResults': function() {return 'No hay datos'}
        }
    })
    if (setToZero) {
        $elem.val('0').trigger('change')
    }
    $('.select2-container').css('width', '100%')
}

var resetStateDropDown = function(geographyGroup, setToZero, data) {resetDropDown($('select#state[geography-group=' + geographyGroup + ']'), data, 'Provincia/Estado', setToZero)}
var resetCityDropDown = function(geographyGroup, setToZero, data) {resetDropDown($('select#city[geography-group=' + geographyGroup + ']'), data, 'Ciudad', setToZero)}
var resetNeighborhoodDropDown = function(geographyGroup, setToZero, data) {resetDropDown($('select#neighborhood[geography-group=' + geographyGroup + ']'), data, 'Barrio/Zona', setToZero)}

var geographyHierarchy

var setUpGeographySelect2 = function(geographyGroup, countrySelectHasOptionsPreloaded, executeAfter) {
    if (countrySelectHasOptionsPreloaded) {
        $('select#country[geography-group=' + geographyGroup + ']').select2({language: {'noResults': function() {return 'No hay datos'}}})
    } else {
        resetDropDown($('select#country[geography-group=' + geographyGroup + ']'), $.map(geographyHierarchy, function(c) {return {id: c.id, text: c.name}}), 'País', true)
        $('select#country[geography-group=' + geographyGroup + ']').val($('select#country[geography-group=' + geographyGroup + ']').attr('value')).trigger('change')
    }
    resetStateDropDown(geographyGroup)
    resetCityDropDown(geographyGroup)
    resetNeighborhoodDropDown(geographyGroup)

    $('select#country[geography-group=' + geographyGroup + ']').change(function() {
        var thisElem = this
        var countryId = parseInt($(thisElem).val())
        geographyGroup = $(thisElem).attr('geography-group')
        if (countryId) {
            $.ajax({
                url: '/crm/geografia/pais/' + countryId + '/estados',
                method: 'GET',
                dataType: 'json',
                success: function(states) {
                    resetStateDropDown(geographyGroup, true, $.map(states, function(s) {return {id: s.id, text: s.name}}))
                    $('select#state[geography-group=' + geographyGroup + ']').val($('select#state[geography-group=' + geographyGroup + ']').attr('value')).trigger('change')
                    $('select#state[geography-group=' + geographyGroup + ']').val($('select#state[geography-group=' + geographyGroup + ']').attr('value', ''))
                    resetCityDropDown(geographyGroup, true)
                    resetNeighborhoodDropDown(geographyGroup, true)
                }
            })
        } else {
            resetStateDropDown(geographyGroup, true)
            resetCityDropDown(geographyGroup, true)
            resetNeighborhoodDropDown(geographyGroup, true)
        }
    })

    $('select#state[geography-group=' + geographyGroup + ']').change(function() {
        var thisElem = this
        var countryId = parseInt($(thisElem).val())
        geographyGroup = $(thisElem).attr('geography-group')
        if (countryId) {
            $.ajax({
                url: '/crm/geografia/estado/' + countryId + '/ciudades',
                method: 'GET',
                dataType: 'json',
                success: function(cities) {
                    resetCityDropDown(geographyGroup, true, $.map(cities, function(c) {return {id: c.id, text: c.name}}))
                    $('select#city[geography-group=' + geographyGroup + ']').val($('select#city[geography-group=' + geographyGroup + ']').attr('value')).trigger('change')
                    $('select#city[geography-group=' + geographyGroup + ']').val($('select#city[geography-group=' + geographyGroup + ']').attr('value', ''))
                    resetNeighborhoodDropDown(geographyGroup, true)
                }
            })
        } else {
            resetCityDropDown(geographyGroup, true)
            resetNeighborhoodDropDown(geographyGroup, true)
        }
    })

     $('select#city[geography-group=' + geographyGroup + ']').change(function() {
        var thisElem = this
        var countryId = parseInt($(thisElem).val())
        geographyGroup = $(thisElem).attr('geography-group')
        if (countryId) {
            $.ajax({
                url: '/crm/geografia/ciudad/' + countryId + '/barrios',
                method: 'GET',
                dataType: 'json',
                success: function(neighborhoods) {
                    resetNeighborhoodDropDown(geographyGroup, true, $.map(neighborhoods, function(n) {return {id: n.id, text: n.name}}))
                    $('select#neighborhood[geography-group=' + geographyGroup + ']').val($('select#neighborhood[geography-group=' + geographyGroup + ']').attr('value')).trigger('change')
                    $('select#neighborhood[geography-group=' + geographyGroup + ']').val($('select#neighborhood[geography-group=' + geographyGroup + ']').attr('value', ''))
                }
            })
        } else {
            resetNeighborhoodDropDown(geographyGroup, true)
        }
    })

    $('select#country[geography-group=' + geographyGroup + ']').trigger('change')
    if (executeAfter) {executeAfter()}
}

var setUpGeographyHierarchies = function(geographyGroup, countrySelectHasOptionsPreloaded, executeAfter) {
    if (!geographyHierarchy) {
        $.ajax({
            url: '/crm/geografia/paises',
            method: 'GET',
            dataType: 'json',
            success: function(data) {
                geographyHierarchy = data
                setUpGeographySelect2(geographyGroup, countrySelectHasOptionsPreloaded, executeAfter)
            }
        })
    } else {
        setUpGeographySelect2(geographyGroup, countrySelectHasOptionsPreloaded, executeAfter)
    }
}
//Geography hierarchies set up

//Log Out
$('a.logout').click(function() {
    $.ajax({
        url: '/crm/logout_usuario',
        method: 'POST'
    })
})
//Log Out

//Search logic
var latestSearchTerm

var searchKeyUp = function() {
    var searchValue = $(this).val()
    if (searchValue) {
        $('a#new-contact-search-result b').text('Nuevo contacto ' + searchValue.toTitleCase())
        $('a#new-contact-search-result').attr('href', '/crm/crear_contacto/nombre/' + searchValue.toTitleCase())
    } else {
        $('a#new-contact-search-result b').text('Nuevo contacto')
        $('a#new-contact-search-result').attr('href', '/crm/nuevo_contacto')
    }
}

var searchKeyDown = function(e, thisElem, searchItemClass, $searchBox) {
    //Arrow up
    if (e.which === 38) {
        e.preventDefault()
        $priorItems = $(searchItemClass).filter(function(k, e) {return parseInt($(e).attr('search-item-order')) < parseInt($(thisElem).attr('search-item-order'))})
        if ($priorItems.length > 0) {
            $($priorItems.sort(function(x, y) {return parseInt($(x).attr('search-item-order')) > parseInt($(y).attr('search-item-order')) ? -1 : 1})[0]).focus()
        }
    }

    //Arrow down
    if (e.which === 40) {
        e.preventDefault()
        $laterItems = $(searchItemClass).filter(function(k, e) {return parseInt($(e).attr('search-item-order')) > parseInt($(thisElem).attr('search-item-order'))})
        if ($laterItems.length > 0) {
            $($laterItems.sort(function(x, y) {return parseInt($(x).attr('search-item-order')) > parseInt($(y).attr('search-item-order')) ? 1 : -1})[0]).focus()
        }
    }

    //Escape
    if (e.which === 27) {
        e.preventDefault()
        $searchBox.val('').focus()
    }
}

var searchFocusOut = function() {
    //If after 300ms the focused element is not one of the search results or the search box itself (.search-item) then the results are hidden
    setTimeout(function() {
        if (!$(document.activeElement).hasClass('search-item')) {
            $('.search-results-container').hide()
        }
    }, 300)
}

var searchItemFocus = function() {
    $('div.search-result').removeClass('focused')
    $(this).parents('div.search-result').addClass('focused')
}

var searchResultHover = function() {
    $(this).find('a.search-item').trigger('focusin')
}

var contactsPropertiesSearch = function(e, thisElem, $resultsContainer) {
    searchTerm = $(thisElem).val()
    if (searchTerm && searchTerm != latestSearchTerm && searchTerm.length > 1) {
        latestSearchTerm = searchTerm
        $resultsContainer.show()
        if ($resultsContainer.find('.search-results img.ajax-wait').length == 0) {$resultsContainer.find('.search-results').prepend($('<div/>', {style: 'heigth: 50px;'}).append($('<img/>', {class: 'ajax-wait', src: '/static/collaborative_crm/images/misc/ajax.gif', height: 40, width: 60})))}
        $.ajax({
            url: '/crm/buscar/html/contactos-propiedades/' + searchTerm,
            method: 'GET',
            dataType: 'html',
            success: function(r) {
                $resultsContainer.find('.search-results').replaceWith(r)
                //$('div.search-result').click(searchResultClick).hover(searchResultHover)
                $('div.search-result').click(showPropertySearchResultModal).hover(searchResultHover)
                $('div.search-result a.search-item').click(showPropertySearchResultModal).focusout(searchFocusOut).keydown(function(e) {searchKeyDown(e, this, '.search-item', $('input#search-box'))}).focusin(searchItemFocus).hover(function() {$($(this).trigger('focusin'))})
                $('a#new-contact-search-result').attr('search-item-order', $('div.search-result').length)
                $('input#search-box').focus()
            }
        })
    } else {
        if (!searchTerm || searchTerm.length <= 1) {
            $resultsContainer.hide()
        } else if (searchTerm == latestSearchTerm && e.keyCode != 13) {
            $resultsContainer.show()
        } else if (e.keyCode == 13) {
            $($('.search-result a')[0]).trigger('click')
        }
    }
}

//Contact details modal
$('#contact-details-modal').on('shown.bs.modal', function() {
    $('#contact-details-modal .modal-body').scrollTop(0)
})

var contactModalContactPropertyRelationshipCommentary
var contactModalContactPropertyRelationshipCommentarySave = function() {
    var thisElem = this
    if ($(thisElem).val() != contactModalContactPropertyRelationshipCommentary) {
        $.ajax({
            url: '/crm/contacto/' + $(thisElem).attr('contact-id') + '/propiedad/' + $(thisElem).attr('property-id') + '/actualizar_datos',
            method: 'POST',
            data: JSON.stringify({'commentary': $(thisElem).val()}),
            dataType: 'json',
            success: function(r) {
                if (r.status == 'Ok') {
                    contactModalContactPropertyRelationshipCommentary = $(thisElem).val()
                    $('#contact-details-modal #last-modified-datetime p.value').text(r.last_modified_datetime)
                    $(thisElem).parent().removeClass('has-error').addClass('has-success')
                    $('#contact-details-modal #last-modified-datetime p.value').css('color', '#00a65a').css('font-weight', 'bold')
                    setTimeout(function() {
                        $(thisElem).parent().removeClass('has-success')
                        $('#contact-details-modal #last-modified-datetime p.value').css('color', 'black').css('font-weight', 'normal')
                    }, 4000)

                } else {
                    $(thisElem).parent().removeClass('has-success').addClass('has-error')
                }
            }
        })
    }
}

var showContactDetailsModal = function(contactId, propertyId, unbindFunction) {
    $.ajax({
        url: '/crm/contacto/' + contactId + (parseInt(propertyId) ? ('/propiedad/' + propertyId) : '') + '/modal',
        method: 'GET',
        dataType: 'html',
        success: function(modal) {
            $('#contact-details-modal').replaceWith(modal)

            if (parseInt(propertyId)) {
                contactModalContactPropertyRelationshipCommentary = $('#contact-details-modal textarea#commentary').val()
                $('#contact-details-modal textarea#commentary').focusout(contactModalContactPropertyRelationshipCommentarySave)
                $('#contact-details-modal button.unbind').click(unbindFunction).attr('contact-id', contactId)
            }

            $('#contact-details-modal').modal('show')
        }
    })
}
//Contact details modal

//Property details modal
$('#property-details-modal').on('shown.bs.modal', function() {
    $('#property-details-modal .modal-body').scrollTop(0)
})

var propertyModalContactPropertyRelationshipCommentary
var propertyModalContactPropertyRelationshipCommentarySave = function(thisElem, property_id) {
    if ($(thisElem).val() != propertyModalContactPropertyRelationshipCommentary) {
        $.ajax({
            url: '/crm/contacto/' + $('form#contact-info').attr('contact-id') + '/propiedad/' + property_id + '/actualizar_datos',
            method: 'POST',
            data: JSON.stringify({'commentary': $(thisElem).val()}),
            dataType: 'json',
            success: function(r) {
                if (r.status == 'Ok') {
                    propertyModalContactPropertyRelationshipCommentary = $(thisElem).val()
                    $('#property-details-modal #last-modified-datetime p.value').text(r.last_modified_datetime)
                    $(thisElem).parent().removeClass('has-error').addClass('has-success')
                    $('#property-details-modal #last-modified-datetime p.value').css('color', '#00a65a').css('font-weight', 'bold')
                    setTimeout(function() {
                        $(thisElem).parent().removeClass('has-success')
                        $('#property-details-modal #last-modified-datetime p.value').css('color', 'black').css('font-weight', 'normal')
                    }, 4000)

                } else {
                    $(thisElem).parent().removeClass('has-success').addClass('has-error')
                }
            },
        })
    }
}

var showPropertyDetailsModal = function(property_id, contactId, bindFunction, unbindFunction) {
    $.ajax({
        url: '/crm/propiedad/' + property_id + (contactId ? ('/contacto/' + contactId) : '') + '/modal',
        method: 'GET',
        dataType: 'html',
        success: function(modal) {
            $('#property-details-modal').replaceWith(modal)

            propertyModalContactPropertyRelationshipCommentary = $('#property-details-modal textarea#commentary').val()
            $('#property-details-modal textarea#commentary').focusout(function() {propertyModalContactPropertyRelationshipCommentarySave(this, property_id)})

            $('#property-details-modal #property-cover-img.no-images').unbind('click').css('cursor', 'default')
            $('#property-details-modal #property-cover-img.images').unbind('click').css('cursor', 'pointer').click(function() {
                    $('#blueimp-gallery').data('useBootstrapModal', false).data('fullScreen', true)
                    blueimp.Gallery($('#property-details-modal div#blueimp-links a'), $('#blueimp-gallery').data())
                })

            $('#property-details-modal button.unbind').unbind('click')
            if (unbindFunction) {
                $('#property-details-modal button.unbind').click(unbindFunction).attr('property-id', property_id)
            }

            $('#property-details-modal button.bind.interested, #property-details-modal button.bind.owner').unbind('click')
            if (bindFunction) {
                $('#property-details-modal button.bind.interested, #property-details-modal button.bind.owner').click(bindFunction).attr('property-id', property_id)
            }

            $('button.property-file-button').unbind('click').click(function() {
                showFileModal($(this).attr('property-id'), contactId ? contactId : null)
            })

            $('#property-details-modal').modal('show')
        }
    })
}

$('#property-details-modal').on('shown.bs.modal', function() {
    $('#property-details-modal .modal-body').scrollTop(0)
})
//Property details modal

//History logic
var showHistoryDetails = function() {
    var thisElem = this
    historyEntryId = $(thisElem).attr('history-entry-id')
    $.ajax({
        url: '/crm/' + $(thisElem).attr('object-type') + '/' + $(thisElem).attr('object-id') + '/historia/' + historyEntryId + '/modal',
        method: 'GET',
        dataType: 'html',
        success: function(modal) {
            $('#history-details-modal').replaceWith(modal)
            $('#history-details-modal').modal('show')
        }
    })
}

var historyFilters = {}

var setUpHistoryLogic = function($clickables, objectType, objectId) {

    $('a#show-filter-history').click(function() {
        $('#filter-history-modal').modal('show')
    })

    $('#history-details-modal').on('shown.bs.modal', function() {
        $('#history-details-modal .modal-body').scrollTop(0)
    })

    $clickables.attr('object-type', objectType).attr('object-id', objectId).click(showHistoryDetails)

    var showMoreHistory = function() {
        $.ajax({
            url: '/crm/' + objectType + '/' + objectId + '/historia/' + ($('.box-body.history div.item').length + 10).toString() + '-' + ($('.box-body.history div.item').length + 1).toString(),
            method: 'POST',
            data: JSON.stringify(historyFilters),
            dataType: 'html',
            success: function (data) {
                if ($('#show-more-history').length > 0) {
                    $('#show-more-history').replaceWith(data)
                } else {
                    $('.box-body.history').append(data)
                }

                $('#show-more-history').click(showMoreHistory)
                $('a.name.history').unbind('click').click(showHistoryDetails)
            }
        })
    }

    var setUpHistoryFilters = function(clear) {
        if (clear) {
            $('#filter-history-modal i.clear-values').trigger('click')
        }
        historyFilters = {
            timestamp__gte: $('#filter-history-modal input#date-from').data('DateTimePicker').date() ? $('#filter-history-modal input#date-from').data('DateTimePicker').date()._d : null,
            timestamp__lte: $('#filter-history-modal input#date-to').data('DateTimePicker').date() ? $('#filter-history-modal input#date-to').data('DateTimePicker').date()._d : null,
            type_id__in: $('#filter-history-modal select#types').val(),
            user_id__in: $('#filter-history-modal select#users').val()
        }
    }

    $('#show-more-history').click(showMoreHistory)
    $('button#filter-history').click(function() {
        setUpHistoryFilters()
        $('.box-body.history div.item').remove()
        showMoreHistory()
    })
    $('#remove-history-filters').click(function() {
        setUpHistoryFilters(true)
        $('.box-body.history div.item').remove()
        showMoreHistory()
    })
}

$('#filter-history-modal input').datetimepicker({locale: 'es'})
$('#filter-history-modal select').select2({language: {'noResults': function() {return 'No hay datos'}}})
$('#filter-history-modal').on('shown.bs.modal', function() {
    $('.select2-container').css('width', '100%')
})

$('i.clear-values').click(function(e) {
    var thisElem = this
    e.preventDefault()
    if ($(thisElem).parents('.form-group').find('.bootstrap-datetimepicker-widget').length > 0) {
        $(thisElem).parents('.form-group').find('input').data('DateTimePicker').date(null)
    } else {
        $(thisElem).parents('.form-group').find('input, select').val(undefined).trigger('change')
    }
})
//History logic

//Workaround
$originalDiv = $('.search-results-container .search-results')
$clonedDiv = $originalDiv.clone()
$originalDiv.parent().parent().prepend($clonedDiv)
$originalDiv.parent().remove()

$originalDiv = $('.search-results-container')
$clonedDiv = $originalDiv.clone()
$($originalDiv.parent().find('a')[0]).append($clonedDiv)
$originalDiv.remove()

$('div.search-result a:not(.search-item)').remove()
//Workaround

var showPropertySearchResultModal = function(e) {
    var thisElem = this
    var $thisElem = $(thisElem).hasClass('search-item') ? $(thisElem) : $(thisElem).find('a.search-item')
    e.preventDefault()
    if ($thisElem.attr('type') == 'property') {
        showPropertyDetailsModal($thisElem.attr('id'), parseInt($('form#contact-info').attr('contact-id')), bindPropertyToContactSearch, unbindPropertyFromContactSearch)
    } else {
        window.location.href = $thisElem.attr('href')
    }
    return false
}

$('input#search-box').keyup(searchKeyUp).keyup($.throttle(750, function(e) {contactsPropertiesSearch(e, this, $('.search-results-container'))})).focusout(searchFocusOut).keydown(function(e) {searchKeyDown(e, this, '.search-item', $('input#search-box'))}).focusin(function() {if($(this).val()) {$('.search-results-container').show()}})
$('a#new-contact-search-result').focusout(searchFocusOut).keydown(function(e) {searchKeyDown(e, this, '.search-item', $('input#search-box'))}).focusin(searchItemFocus).hover(function() {$($(this).trigger('focusin'))})
//$('a#new-property-search-result').focusout(searchFocusOut).keydown(function(e) {searchKeyDown(e, this, '.search-item', $('input#search-box'))}).focusin(searchItemFocus).hover(function() {$($(this).trigger('focusin'))})
//$('div.search-result').click(searchResultClick).hover(searchResultHover)
$('div.search-result').click(showPropertySearchResultModal).hover(searchResultHover)
//Search logic

//Property search-results show modal
var unbindPropertyFromContactSearch = function() {
    var propertyId = $(this).attr('property-id')
    $.ajax({
        url: '/crm/contacto/' + $('form#contact-info').attr('contact-id') + '/propiedad/' + propertyId + '/desvincular',
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
}

var bindPropertyToContactSearch = function() {
    var thisElem = this
    var propertyId = $(thisElem).attr('property-id')
    var relType = $(thisElem).hasClass('owner') ? 'dueno' : 'interesado'
    $.ajax({
        url: '/crm/contacto/' + $('form#contact-info').attr('contact-id') + '/propiedad/' + propertyId + '/vincular/' + relType,
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
//Property search-results show modal

//Company logo upload
$(function() {
    Dropzone.options.uploadCompanyLogoBasePage = {
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

//Notifications
var seeNotification = function() {
    var id = $(this).attr('id')
    $.ajax({
        url: id == 'see-all-notifications' ? ('/crm/notificaciones/ver_todas') : ('/crm/notificacion/' + id + '/ver'),
        method: 'POST',
        dataType: 'json',
        success: function(r) {
            if (r.status == 'Ok') {
                if (r.url) {
                    window.location.href = r.url
                } else {
                    if (id == 'see-all-notifications') {
                        $('li.notification').removeClass('unseen')
                    } else {
                        $('li.notification[id=' + id + ']').removeClass('unseen')
                    }
                    $('span.label.label-warning').text(r.unseen_notifications_count)
                    if (!r.unseen_notifications_count) {$('span.label.label-warning').hide()}
                }
            } else {
                alert(r.exception_class + ' - ' + r.exception_message)
            }
        }
    })
}

$('li.notification, #see-all-notifications').click(seeNotification)
//Notifications

//Excel/PDF logic
var excelFileAttributes = function() {
    return [
        $('#file-modal input#hide-exact-address').prop('checked') ? 'ocultar-direccion-exacta' : '',
        !$('#file-modal input#include-images').prop('checked') ? 'no-incluir-imagenes' : '',
        !$('#file-modal input#include-cover-image').prop('checked') ? 'no-incluir-imagen-portada' : ''
    ].join('-').replace('--', '')
}

var enableDisableSendEmailButton = function() {
    $('#file-modal button#send-email').prop('disabled', !($('#file-modal select#users-to').val() || $('#send-to-myself').prop('checked')))
}

var filesModalSendEmail = function() {
    $.ajax({
        url: '/crm/propiedad/' + $('#file-modal').attr('property-id') + '/' + ($('input#pdf-format').prop('checked') ? 'pdf' : 'excel') + (excelFileAttributes() ? ('/' + excelFileAttributes()) : '') + '/email',
        method: 'POST',
        dataType: 'json',
        data: JSON.stringify({
            contacts_to: $('#file-modal select#users-to').val() ? $.map($('#file-modal select#users-to').val().filter(function(e) {return e.indexOf('contact-') > -1}), function(e) {return parseInt(e.replace('contact-', ''))}) : [],
            users_to: $('#file-modal select#users-to').val() ? $.map($('#file-modal select#users-to').val().filter(function(e) {return e.indexOf('user-') > -1}), function(e) {return parseInt(e.replace('user-', ''))}) : [],
            send_to_myself: $('#file-modal input#send-to-myself').prop('checked'),
            include_email: $('#file-modal input#include-email').prop('checked'),
            include_telephone_number: $('#file-modal input#include-telephone-number').prop('checked'),
            message: $('#file-modal textarea#email-message').val()
        }),
        success: function(r) {
            if (r.status == 'Ok') {
                //do nothing
            } else {
                alert('Error al enviar mails: ' + r.exception_class + ' - ' + r.exception_message)
            }
        }
    })
    $('#file-modal textarea#email-message').val('')
    $('#file-modal').modal('hide')
}

var showFileModal = function(propertyId, selectedContactId) {
    $.ajax({
        url: '/crm/propiedad/' + propertyId + '/modal_fichas' + (selectedContactId ? ('/contacto/' + selectedContactId) : ''),
        method: 'GET',
        dataType: 'html',
        success: function(modal) {
            $('#file-modal').replaceWith(modal)

            $('#file-modal').on('shown.bs.modal', function() {
                $('.select2-container').css('width', '100%')
            })

            $('input#excel-format').change(function() {
                if (!$('input#excel-format').prop('checked') && !$('input#pdf-format').prop('checked')) {
                    $('input#excel-format').parent().toggleClass('active')
                    $('input#excel-format').prop('checked', !$('input#excel-format').prop('checked'))
                } else {
                    $('input#pdf-format').parent().toggleClass('active')
                    $('input#pdf-format').prop('checked', !$('input#pdf-format').prop('checked'))
                }
            })

            $('input#pdf-format').change(function() {
                if (!$('input#pdf-format').prop('checked') && !$('input#excel-format').prop('checked')) {
                    $('input#pdf-format').parent().toggleClass('active')
                    $('input#pdf-format').prop('checked', !$('input#pdf-format').prop('checked'))
                } else {
                    $('input#excel-format').parent().toggleClass('active')
                    $('input#excel-format').prop('checked', !$('input#excel-format').prop('checked'))
                }
            })

            $('#file-modal button#download').click(function() {
                window.location.href = '/crm/propiedad/' + $('#file-modal').attr('property-id') + '/' + ($('input#pdf-format').prop('checked') ? 'pdf' : 'excel') + (excelFileAttributes() ? ('/' + excelFileAttributes()) : '') + '/' + $(this).attr('file-name') + ($('input#pdf-format').prop('checked') ? '.pdf' : '.xlsx')
            })

            $('#file-modal select#users-to').select2({language: {'noResults': function() {return 'No hay datos'}}})

            $('#file-modal select#users-to').change(enableDisableSendEmailButton)
            $('#send-to-myself').change(enableDisableSendEmailButton)

            $('#file-modal button#clean-users-to-selection').click(function() {
                $('#file-modal select#users-to').val([]).trigger('change')
            })

            $('#file-modal button#include-all-interested').click(function() {
                interestedContacts = $.map($('#file-modal select#users-to option.interested[type=contact]'), function(e) {return $(e).attr('value')})
                newValue = $('#file-modal select#users-to').val() ? $('#file-modal select#users-to').val().concat(interestedContacts).unique() : interestedContacts
                $('#file-modal select#users-to').val(newValue).trigger('change')
            })

            $('#file-modal button#include-all-users').click(function() {
                allUsers = $.map($('#file-modal select#users-to option[type=user]'), function(e) {return $(e).attr('value')})
                newValue = $('#file-modal select#users-to').val() ? $('#file-modal select#users-to').val().concat(allUsers).unique() : allUsers
                $('#file-modal select#users-to').val(newValue).trigger('change')
            })

            $('#file-modal button#send-email').click(filesModalSendEmail)

            $('#file-modal').modal('show')
        }
    })
}
//Excel/PDF logic

//Sounds
var playSound = function (toneId) {
    if (toneId) {
        $audio = $('<audio/>', {autoplay: 'autoplay'})
                    .append($('<source/>', {id: 'mp3', src: '/crm/tonos/mp3/' + toneId, type: 'audio/mpeg'}))
                    .append($('<source/>', {id: 'ogg', src: '/crm/tonos/ogg/' + toneId, type: 'audio/ogg'}))
                    .append($('<embed/>', {id: 'mp3', hidden: 'true', autostart: 'true', loop: 'false', src: '/crm/tonos/mp3/' + toneId}))
        $('div#sound').empty().append($audio)
    }
}

var playNotificationTone = function () {
    playSound(parseInt($('meta#user').attr('notifications-tone-id')))
}

var playMessagesTone = function () {
    playSound(parseInt($('meta#user').attr('messages-tone-id')))
}
//Sounds

//Updates
////Desktop notifications
document.addEventListener('DOMContentLoaded', function () {
  if (Notification.permission !== 'granted')
    Notification.requestPermission()
})

var desktopNotify = function (title, body, href, iconSrc, closeOnClick, closeAfterNSeconds) {
    closeOnClick = closeOnClick === undefined ? true : closeOnClick
    closeMsegs = closeAfterNSeconds ? (closeAfterNSeconds * 1000) : 5000

//    if (!Notification) {
//        alert('Las notificaciones de escritorio no estan disponibles en su navegador.')
//        return
//    }

    if (Notification.permission !== 'granted')
        Notification.requestPermission()
    else {
        var notification = new Notification(title, {
          icon: iconSrc,
          body: body
        })
        setTimeout(notification.close.bind(notification), closeMsegs)
        if (href) {
            notification.onclick = function () {
              window.open(href)
//              if (closeOnClick) {
//                notification.close.bind(notification)
//              }
            }
        }
    }
}
////Desktop notifications

////Websocket
ws_scheme = window.location.protocol == 'https:' ? 'wss' : 'ws'
socket = new WebSocket(ws_scheme + '://' + window.location.host + '/updates/')

var notificationDefaultAction = function(data) {
    $('li#notifications').replaceWith(data.html)
    $('li.notification, #see-all-notifications').click(seeNotification)
    playNotificationTone()
    $('span#unseen-notifications').parent().effect('bounce', {times: 10, distance:10}, 2000)
    desktopNotify(data.title, data.short_description, data.fully_qualified_url, data.image_src, true, 5)
}

var notificationAction = function(data) {
    notificationDefaultAction(data)
}

var messageDefaultAction = function(data) {
    $('li#messages').replaceWith(data.html)
    playMessagesTone()
    $('span#unred-messages').parent().effect('bounce', {times: 10, distance:10}, 2000)
    desktopNotify(data.conversation, data.from + ': ' + data.content, data.fully_qualified_url, data.image_src, true, 5)
}

var messageAction = function(data) {
    messageDefaultAction(data)
}

socket.onmessage = function(e) {
    data = JSON.parse(e.data)
    switch (data.update_type) {
        case 'notification':
            notificationAction(data)
            break
        case 'message':
            messageAction(data)
            break
    }
}
////Websocket
//Updates
