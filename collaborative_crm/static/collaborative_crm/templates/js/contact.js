//slimScroll set up
$(function(){
    $('.box-body.properties, .box-body.searches, .box-body.history').slimScroll({
        height: '250px'
    })
})
//slimScroll set up

//create contact/edit on change logic
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
        $elem.tooltipster('update', 'El nombre debe informarse antes de guardar ')
        $elem.tooltipster('show')
        $elem.unbind('focusin').focusin(function() {
            thisElem = this
            $(thisElem).tooltipster('hide')
            $(thisElem).unbind('focusin').unbind('click')
        })
    }
}

var saveContact = function() {
//    if (($('.mandatory-group-1').filter(function(k, e) {return !$(e).val() || ['', '0', '-1'].indexOf($(e).val()) > -1}).length > 0) && ($('.mandatory-group-2').filter(function(k, e) {return !$(e).val() || ['', '0', '-1'].indexOf($(e).val()) > -1}).length > 0)) {
//        $.each($('.mandatory'), function(k, e) {showMandatoryToolTip(e)})
    if ($('.mandatory').filter(function(k, e) {return !$(e).val() || ['', '0', '-1'].indexOf($(e).val()) > -1}).length > 0) {
        $.each($('.mandatory'), function(k, e) {showMandatoryToolTip(e)})
    } else {
        if ($('a#property-owner').attr('property-id')) {$('form#contact-info').append($('<input/>', {type: 'hidden', name: 'property-owner-id'}).val($('a#property-owner').attr('property-id')))}
        if ($('a#property-interested').attr('property-id')) {$('form#contact-info').append($('<input/>', {type: 'hidden', name: 'property-interested-id'}).val($('a#property-interested').attr('property-id')))}
        $('#created-contact-modal').modal('show')
        setTimeout(function() {
            $('form#contact-info').submit()
        }, 2500)
    }
}

if ($('form#contact-info').attr('contact-id') != '0') {
    editOnChangeControlsCurrentValues = $.map($('.edit-on-change'), function(c) {return {control: $(c).attr('id'), currentValue: $(c).val()}})

    var save = function(thisElem, saveBlank) {
        if ((($(thisElem).val() && $(thisElem).val() != '') || saveBlank) && $(thisElem).val() != editOnChangeControlsCurrentValues.filter(function(v) {return v.control == $(thisElem).attr('id')})[0].currentValue) {
            $(thisElem).parent().removeClass('has-warning')
            //if ((saveBlank && (!$(thisElem).val() || $(thisElem).val() == '') && $(thisElem).hasClass('mandatory')) && (($('.mandatory-group-1').filter(function(k, e) {return !$(e).val() || ['', '0', '-1'].indexOf($(e).val()) > -1}).length > 0) && ($('.mandatory-group-2').filter(function(k, e) {return !$(e).val() || ['', '0', '-1'].indexOf($(e).val()) > -1}).length > 0))) {
            if ((saveBlank && (!$(thisElem).val() || $(thisElem).val() == '') && $(thisElem).hasClass('mandatory')) && ($('.mandatory').filter(function(k, e) {return !$(e).val() || ['', '0', '-1'].indexOf($(e).val()) > -1}).length > 0)) {
                showMandatoryToolTip(thisElem)
            } else {
                $.ajax({
                    url: '/crm/contacto/' + $('form#contact-info').attr('contact-id') + '/actualizar_campo',
                    method: 'POST',
                    data: JSON.stringify({fieldName: $(thisElem).attr('id'), fieldValue: $(thisElem).val()}),
                    dataType: 'json',
                    success: function(r) {
                        if (r.status == 'Ok') {
                            if (r.change) {
                                $(thisElem).parent().addClass('has-success')
                                editOnChangeControlsCurrentValues.filter(function(v) {return v.control == $(thisElem).attr('id')})[0].currentValue = $(thisElem).val()
                                setTimeout(function() {
                                    $(thisElem).parent().removeClass('has-success')
                                }, 4000)
                            }
                        } else {
                            $(thisElem).parent().addClass('has-error')
                        }
                    }
                })
            }
        }
    }

    $('.edit-on-change').keyup(
        function(e) {
            if ([9, 13, 27].indexOf(e.keyCode) == -1) {
                thisElem = $(this)
                if ($(thisElem).val() != editOnChangeControlsCurrentValues.filter(function(v) {return v.control == $(thisElem).attr('id')})[0].currentValue) {
                    $(thisElem).parent().removeClass('has-success')
                    $(thisElem).parent().removeClass('has-error')
                    $(thisElem).parent().addClass('has-warning')
                } else {
                    $(thisElem).parent().removeClass('has-warning')
                }
            } else {
                if (e.keyCode == 13) {
                    save(thisElem, true)
                }
            }
        }
    )

    $('.edit-on-change').focusout(function() {save(this, false)})
} else {
    $('.edit-on-change').focusout(saveContact)
}
//create contact/edit on change logic

//History logic
setUpHistoryLogic($('a.name.history'), 'contacto', $('form#contact-info').attr('contact-id'))
//History logic

//Properties logic
var unbindPropertyFromContact = function() {
    var propertyId = $(this).attr('property-id')
    $.ajax({
        url: '/crm/contacto/' + $('form#contact-info').attr('contact-id') + '/propiedad/' + propertyId + '/desvincular',
        method: 'DELETE',
        dataType: 'json',
        success: function(r) {
            if (r.status == 'Ok') {
                $('a.name.property[property-id=' + propertyId + ']').parents('div.item').remove()
                $('a.search-result-show-property-details[property-id=' + propertyId + ']')
                    .unbind('click')
                    .click(function() {showPropertyDetails(this)})
                    .parents('div.box-header').find('span.label').remove()
            } else {
                alert(r.exception_class + ' - ' + r.exception_message)
            }
        }
    })
}

var bindPropertyToContact = function() {
    var thisElem = this
    var propertyId = $(thisElem).attr('property-id')
    var relType = $(thisElem).hasClass('owner') ? 'dueno' : 'interesado'
    $.ajax({
        url: '/crm/contacto/' + $('form#contact-info').attr('contact-id') + '/propiedad/' + propertyId + '/vincular/' + relType,
        method: 'POST',
        dataType: 'json',
        success: function(r) {
            if (r.status == 'Ok') {
                $('div.box-body.properties').prepend(createPropertyItemDiv(r.property))
                $('a.search-result-show-property-details[property-id=' + propertyId + ']')
                    .unbind('click')
                    .click(showPropertyDetails)
                    .parents('div.box-header').append('&nbsp;&nbsp;').append($('<span/>', {class: 'label label-' + (relType == 'dueno' ? 'warning' : 'success'), text: relType == 'dueno' ? 'Dueño' : 'Interesado'}))
            } else {
                alert(r.exception_class + ' - ' + r.exception_message)
            }
        }
    })
}

var showPropertyDetails = function (thisElem) {
    if (!thisElem) {
        thisElem = this
    }
    showPropertyDetailsModal($(thisElem).attr('property-id'), parseInt($('form#contact-info').attr('contact-id')), bindPropertyToContact, unbindPropertyFromContact)
}

var showRelatedPropertyDetails = function() {
    showPropertyDetailsModal($(this).attr('property-id'), parseInt($('form#contact-info').attr('contact-id')), bindPropertyToContactSearch, unbindPropertyFromContactSearch)
}

$('a.name.property').click(showRelatedPropertyDetails)

var createPropertyItemDiv = function(p) {
    var $itemDiv = $('<div/>', {class: 'item'})

    $a = $('<a/>', {class: 'name property', 'property-id': p.property.id}).append($('<small/>', {class: 'text-muted pull-right'}).append($('<i/>', {class: 'fa fa-home'})).append(' ' + p.relationship_type)).append(p.property.name)
    $a.click(showRelatedPropertyDetails)
    $pMessage = $('<p/>', {class: 'message'}).append($a).append($('<small/>', {text: !p.commentary ? 'Sin comentarios' : (p.commentary.length <= 100 ? p.commentary : (p.commentary.substring(0, 100) + '...'))}))
    $itemDiv.append($('<img/>', {src: p.property.cover_image_url ? p.property.cover_image_url : '/static/collaborative_crm/images/misc/default_property.png', alt: 'user image', class: 'online'})).append($pMessage)

    return $itemDiv
}

$('#show-more-properties').click(function() {
    $.ajax({
        url: '/crm/contacto/' + $('form#contact-info').attr('contact-id') + '/propiedades/' + ($('.box-body.properties div.item').length + 10).toString() + '-' + ($('.box-body.properties div.item').length + 1).toString(),
        method: 'GET',
        dataType: 'json',
        success: function (data) {
            $.each(data.properties, function(k, p) {
                    $showMore = $('#show-more-properties').before(createPropertyItemDiv(p))
                }
            )
            if ($('.box-body.properties div.item').length >= data.total_properties_count) {
                $showMore.remove()
            }
        }
    })
})
//Properties logic

//Searches logic
$('a.name.search').click(function() {showSearchDetails(this, false, true, true, true)})
$('a#new-search').click(function() {showSearchDetails(this, false, true, true, true, 'Nueva Búsqueda')})

$('a#change-search-parameters, a#change-search-commentary').click(function() {
    $('.select2-container').css('width', '100%')
    $targetBox = $(this).attr('id') == 'change-search-parameters' ? $('#search-parameters-box') : $('#search-commentary-box')
    if ($targetBox.hasClass('collapsed-box')) {$targetBox.find('button[data-widget=collapse]').trigger('click')}
    if (!$('#search-results-box').hasClass('collapsed-box')) {$('#search-results-box button[data-widget=collapse]').trigger('click')}
    $('#search-modal .modal-body').animate({scrollTop: $targetBox.parent().position().top})
})

var executeSearch = function(useSearchParameters, parametersChanged) {
    useSearchParameters = useSearchParameters ? useSearchParameters : false
    parametersChanged = parametersChanged ? parametersChanged : false
    $('#search-results-box .box-body').empty()
    $('#search-results-box .box-header a#change-search-parameters, #search-results-box .box-header a#change-search-commentary').hide()
    $('#search-results-box button[data-widget=collapse]').prop('disabled', true)
    $('#search-results-box .box-header').append($('<img/>', {src: '/static/collaborative_crm/images/misc/ajax.gif', height: 40, width: 60}))
    $.ajax({
        url: '/crm/contacto/' + $('form#contact-info').attr('contact-id') + '/buscar_propiedades' + ($('#search-modal').attr('search-id') ? ('/' + $('#search-modal').attr('search-id')) : ''),
        method: 'POST',
        data: JSON.stringify({
        useSearchParameters: useSearchParameters,
        parametersChanged: parametersChanged,
        commentary: $('#search-modal textarea#commentary').val(),
        parameters: [
            {attribute: 'type_id', operation: 'in', values: $('#search-modal select#type').val(), boolean: false},
            {attribute: 'status_id', operation: 'exact', values: $('#search-modal input#status:checked').val() == 'available' ? 1 : 0, boolean: false},

            {attribute: 'expenses', operation: (parseInt($('#search-modal #expenses-to').val())) ? 'range' : 'gte', values: (parseInt($('#search-modal #expenses-to').val())) ? [parseInt($('#search-modal #expenses-from').val()) ? parseInt($('#search-modal #expenses-from').val()) : 0, parseInt($('#search-modal #expenses-to').val())] : (parseInt($('#search-modal #expenses-from').val()) ? parseInt($('#search-modal #expenses-from').val()) : 0), boolean: false},
            {attribute: 'rooms', operation: (parseInt($('#search-modal #rooms-to').val())) ? 'range' : 'gte', values: (parseInt($('#search-modal #rooms-to').val())) ? [parseInt($('#search-modal #rooms-from').val()) ? parseInt($('#search-modal #rooms-from').val()) : 0, parseInt($('#search-modal #rooms-to').val())] : (parseInt($('#search-modal #rooms-from').val()) ? parseInt($('#search-modal #rooms-from').val()) : 0), boolean: false},
            {attribute: 'bathrooms', operation: (parseInt($('#search-modal #bathrooms-to').val())) ? 'range' : 'gte', values: (parseInt($('#search-modal #bathrooms-to').val())) ? [parseInt($('#search-modal #bathrooms-from').val()) ? parseInt($('#search-modal #bathrooms-from').val()) : 0, parseInt($('#search-modal #bathrooms-to').val())] : (parseInt($('#search-modal #bathrooms-from').val()) ? parseInt($('#search-modal #bathrooms-from').val()) : 0), boolean: false},
            {attribute: 'surface', operation: (parseInt($('#search-modal #surface-to').val())) ? 'range' : 'gte', values: (parseInt($('#search-modal #surface-to').val())) ? [parseInt($('#search-modal #surface-from').val()) ? parseInt($('#search-modal #surface-from').val()) : 0, parseInt($('#search-modal #surface-to').val())] : (parseInt($('#search-modal #surface-from').val()) ? parseInt($('#search-modal #surface-from').val()) : 0), boolean: false},
            {attribute: 'covered_surface', operation: (parseInt($('#search-modal #covered-surface-to').val())) ? 'range' : 'gte', values: (parseInt($('#search-modal #covered-surface-to').val())) ? [parseInt($('#search-modal #covered-surface-from').val()) ? parseInt($('#search-modal #covered-surface-from').val()) : 0, parseInt($('#search-modal #covered-surface-to').val())] : (parseInt($('#search-modal #covered-surface-from').val()) ? parseInt($('#search-modal #covered-surface-from').val()) : 0), boolean: false},
            {attribute: 'orientation', operation: 'icontains', values: $('#search-modal input#orientation').val(), boolean: false},
            {attribute: 'age', operation: (parseInt($('#search-modal #age-to').val())) ? 'range' : 'gte', values: (parseInt($('#search-modal #age-to').val())) ? [parseInt($('#search-modal #age-from').val()) ? parseInt($('#search-modal #age-from').val()) : 0, parseInt($('#search-modal #age-to').val())] : (parseInt($('#search-modal #age-from').val()) ? parseInt($('#search-modal #age-from').val()) : 0), boolean: false},
            {attribute: 'garages', operation: (parseInt($('#search-modal #garages-to').val())) ? 'range' : 'gte', values: (parseInt($('#search-modal #garages-to').val())) ? [parseInt($('#search-modal #garages-from').val()) ? parseInt($('#search-modal #garages-from').val()) : 0, parseInt($('#search-modal #garages-to').val())] : (parseInt($('#search-modal #garages-from').val()) ? parseInt($('#search-modal #garages-from').val()) : 0), boolean: false},

            {attribute: 'for_sale', operation: 'exact', values: $('#search-modal input#for-sale:checked').val() == 'all' ? '' : ($('#search-modal input#for-sale:checked').val() == 'yes' ? 'yes' : 'no'), boolean: true},
            {attribute: 'sale_price', operation: (parseInt($('#search-modal #sale-price-to').val())) ? 'range' : 'gte', values: (parseInt($('#search-modal #sale-price-to').val())) ? [parseInt($('#search-modal #sale-price-from').val()) ? parseInt($('#search-modal #sale-price-from').val()) : 0, parseInt($('#search-modal #sale-price-to').val())] : (parseInt($('#search-modal #sale-price-from').val()) ? parseInt($('#search-modal #sale-price-from').val()) : 0), boolean: false},
            {attribute: 'sale_price_usd', operation: (parseInt($('#search-modal #sale-price-usd-to').val())) ? 'range' : 'gte', values: (parseInt($('#search-modal #sale-price-usd-to').val())) ? [parseInt($('#search-modal #sale-price-usd-from').val()) ? parseInt($('#search-modal #sale-price-usd-from').val()) : 0, parseInt($('#search-modal #sale-price-usd-to').val())] : (parseInt($('#search-modal #sale-price-usd-from').val()) ? parseInt($('#search-modal #sale-price-usd-from').val()) : 0), boolean: false},
            {attribute: 'for_rent', operation: 'exact', values: $('#search-modal input#for-rent:checked').val() == 'all' ? '' : ($('#search-modal input#for-rent:checked').val() == 'yes' ? 'yes' : 'no'), boolean: true},
            {attribute: 'rent_price', operation: (parseInt($('#search-modal #rent-price-to').val())) ? 'range' : 'gte', values: (parseInt($('#search-modal #rent-price-to').val())) ? [parseInt($('#search-modal #rent-price-from').val()) ? parseInt($('#search-modal #rent-price-from').val()) : 0, parseInt($('#search-modal #rent-price-to').val())] : (parseInt($('#search-modal #rent-price-from').val()) ? parseInt($('#search-modal #rent-price-from').val()) : 0), boolean: false},
            {attribute: 'rent_price_usd', operation: (parseInt($('#search-modal #rent-price-usd-to').val())) ? 'range' : 'gte', values: (parseInt($('#search-modal #rent-price-usd-to').val())) ? [parseInt($('#search-modal #rent-price-usd-from').val()) ? parseInt($('#search-modal #rent-price-usd-from').val()) : 0, parseInt($('#search-modal #rent-price-usd-to').val())] : (parseInt($('#search-modal #rent-price-usd-from').val()) ? parseInt($('#search-modal #rent-price-usd-from').val()) : 0), boolean: false},
            {attribute: 'city__state__country_id', operation: 'exact', values: parseInt($('#search-modal select#country').val()), boolean: false},
            {attribute: 'city__state_id', operation: 'exact', values: parseInt($('#search-modal select#state').val()), boolean: false},
            {attribute: 'city_id', operation: 'exact', values: parseInt($('#search-modal select#city').val()), boolean: false},
            {attribute: 'neighborhood_id', operation: 'in', values: $('#search-modal select#neighborhood').val(), boolean: false},
            {attribute: 'street', operation: 'icontains', values: $('#search-modal input#street').val(), boolean: false},
            {attribute: 'number', operation: 'icontains', values: $('#search-modal input#number').val(), boolean: false},
            {attribute: 'floor', operation: 'icontains', values: $('#search-modal input#floor').val(), boolean: false},
            {attribute: 'apartment', operation: 'icontains', values: $('#search-modal input#apartment').val(), boolean: false},
            {attribute: 'intersecting_street_1', operation: 'icontains', values: $('#search-modal input#intersecting-streets').val(), boolean: false},
            {attribute: 'intersecting_street_2', operation: 'icontains', values: $('#search-modal input#intersecting-streets').val(), boolean: false},
            {attribute: 'anonymous_address', operation: 'icontains', values: $('#search-modal input#anonymous-address').val(), boolean: false},
            {attribute: 'description', operation: 'icontains', values: $('#search-modal input#description').val(), boolean: false}
        ]}),
        dataType: 'html',
        success: function(r) {
            $('#search-results-box .box-body').empty().append(r)
            $('#search-modal-title').text($('div#search-results').attr('title') + ' - ' + $('div#search-results').attr('date'))
            $('a.search-result-show-property-details').click(function() {
                var thisElem = this
                showPropertyDetails(thisElem)
            })
            $('.remove-search-result').click(function () {$(this).parents('div.result-box-col').remove()})
            $('#search-results-box .box-header img').remove()
            $('#search-results-box .box-header a#change-search-parameters, #search-results-box .box-header a#change-search-commentary').show()
            $('#search-results-box button[data-widget=collapse]').prop('disabled', false)
            if ($('#search-results-box').hasClass('collapsed-box')) {$('#search-results-box button[data-widget=collapse]').trigger('click')}
            $('#search-modal').attr('search-id', $('div#search-results').attr('search-id'))
            $('#search-modal .modal-body').animate({scrollTop: $('#search-modal #search-results-box').parent().position().top})
            contactSearchParametersChanged = false
        }
    })
}

$('button#execute-search').click(function() {executeSearch(false, contactSearchParametersChanged)})
$('#search-modal input[type=text], #search-modal textarea').keydown(function(e) {if (e.keyCode == 13) {executeSearch(false, contactSearchParametersChanged)}})

$('#show-more-searches').click(function() {
    $.ajax({
        url: '/crm/contacto/' + $('form#contact-info').attr('contact-id') + '/busquedas/' + ($('.box-body.searches div.item').length + 10).toString() + '-' + ($('.box-body.searches div.item').length + 1).toString(),
        method: 'GET',
        dataType: 'json',
        success: function (data) {
            $.each(data.searches, function(k, s) {
                    $showMore = $('#show-more-searches')
                    $itemDiv = $('<div/>', {class: 'item'})
                    $a = $('<a/>', {class: 'name search', 'search-id': s.id}).append($('<small/>', {class: 'text-muted pull-right'}).append($('<i/>', {class: 'fa fa-calendar'})).append(' ' + s.date)).append(s.user.full_name)
                    $a.click(showSearchDetails)
                    $pMessage = $('<p/>', {class: 'message'}).append($a).append($('<small/>').append('Búsqueda <b>' + s.id + '</b>: ' + (!s.commentary ? 'Sin comentarios' : (s.commentary.length <= 100 ? s.commentary : (s.commentary.substring(0, 100) + '...')))))
                    $itemDiv.append($('<img/>', {src: '/static/collaborative_crm/images/misc/default_search.png', alt: 'user image', class: 'offline'})).append($pMessage)
                    $showMore.before($itemDiv)
                }
            )
            if ($('.box-body.searches div.item').length >= data.total_searches_count) {
                $showMore.remove()
            }
        }
    })
})

var searchCommentary

var searchCommentarySave = function(thisElem) {
    if ($(thisElem).val() != searchCommentary) {
        $.ajax({
            url: '/crm/contacto/' + $('form#contact-info').attr('contact-id') + '/busqueda/' + $('#search-modal').attr('search-id') + '/actualizar_comentarios',
            method: 'POST',
            data: $(thisElem).val(),
            dataType: 'json',
            success: function(r) {
                if (r.status == 'Ok') {
                    searchCommentary = $(thisElem).val()
                    $(thisElem).parent().removeClass('has-error').addClass('has-success')
                    setTimeout(function() {
                        $(thisElem).parent().removeClass('has-success')
                    }, 4000)

                } else {
                    $(thisElem).parent().removeClass('has-success').addClass('has-error')
                }
            },
        })
    }
}

$('#remove-search').click(function() {$('#remove-search-modal').modal('show')})
$('#confirm-remove-search').click(function() {
    $.ajax({
        url: '/crm/contacto/' + $('form#contact-info').attr('contact-id') + '/busqueda/' + $('#search-modal').attr('search-id') + '/eliminar',
        method: 'DELETE',
        dataType: 'json',
        success: function(r) {
            if (r.status == 'Ok') {
                $('#search-modal').modal('hide')
            } else {
                alert(r.exception_class + ' - ' + r.exception_message)
            }
        }
    })
})
//Searches logic

//Status logic
if ($('div.contact-status-actions-container').length > 0) {
    $('div.contact-status').css('cursor', 'pointer')
    $('div.contact-status').click(function() {
        $('div.contact-status-actions-container').toggle()
    })
    $(document).click(function(e) {
        if ($('div.contact-status-actions-container').css('display') == 'block' && e.target != $('div.contact-status').get(0) && e.target != $('div.contact-status-actions-container').get(0)) {
            $('div.contact-status-actions-container').hide()
        }
    })
    $('div.contact-status-action').click(function() {
        $.ajax({
            url: '/crm/contacto/' + $('form#contact-info').attr('contact-id') + '/estado/ejecutar_accion/' + $(this).attr('action-id'),
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
    })
}
//Status logic

//geography hierarchy logic
var select2onChangeFunction = function() {
    save(this, true)
}

setUpGeographyHierarchies('contact', false, function() {
    if ($('form#contact-info').attr('contact-id') != '0') {
        $('.edit-on-change-select').change(select2onChangeFunction)
        editOnChangeControlsCurrentValues = editOnChangeControlsCurrentValues.concat($.map($('.edit-on-change-select'), function(c) {return {control: $(c).attr('id'), currentValue: $(c).val()}}))
    } else {
        $('.edit-on-change-select').change(saveContact)
    }
})
//geography hierarchy logic

//Assign agent logic
var assignAgentToContact = function() {
    assignAgent($('form#contact-info').attr('contact-id'), $(this).attr('user-id'), 'contacto')
}

$('#assign-me-agent').click(assignAgentToContact)
$('#assign-agent-search').keyup($.throttle(750, function(e) {assignContactsAgentsSearch(e, this, 'agent', 'agentes-a-cargo', $('div#agent-search-results'), assignAgentToContact, 'user-id')})).keydown(function(e) {if (e.which === 27) {$('div#agent-search-results').empty()}; searchKeyDown(e, this, '.assign-agent-search-item', $('input#assign-agent-search'))})

var unassignAgentToContact = function() {assignAgent($('form#contact-info').attr('contact-id'), undefined, 'contacto')}
$('a#unbind-agent').click(unassignAgentToContact)
//Assign agent logic

//Remove logic
$('button#remove-contact').click(function() {$('#remove-contact-modal').modal('show')})
$('button#confirm-remove').click(function() {
    $.ajax({
        url: '/crm/contacto/' + $('form#contact-info').attr('contact-id') + '/eliminar',
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