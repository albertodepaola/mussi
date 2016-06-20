//Assign agent logic
var assignContactsAgentsSearch = function(e, thisElem, assignEntity, searchForObjects, $searchResultsContainer, resultActionOnClick, idField) {
    var searchTerm = $(thisElem).val()
    if (searchTerm && searchTerm.length > 1) {
    if ($searchResultsContainer.find('img.ajax-wait').length == 0) {$searchResultsContainer.prepend($('<div/>', {style: 'heigth: 50px;'}).append($('<img/>', {class: 'ajax-wait', src: '/static/collaborative_crm/images/misc/ajax.gif', height: 40, width: 60})))}
        $.ajax({
            url: '/crm/buscar/' + searchForObjects + '/' + searchTerm + '/4-0',
            method: 'GET',
            dataType: 'json',
            success: function(r) {
                $searchResultsContainer.empty()
                var searchItemOrder = 1
                $.each(r, function(k, result) {
                    $searchResultsContainer.append('<br>').append($('<a/>', {href: '#', class: 'assign-' + assignEntity + '-search-item', 'search-item-order': searchItemOrder++}).attr(idField, result.id).append(result.full_name).click(resultActionOnClick).keydown(function(e) {if (e.which === 27) {$searchResultsContainer.empty()}; searchKeyDown(e, this, '.assign-' + assignEntity + '-search-item', $('input#assign-' + assignEntity + '-search'))}))
                })
            }
        })
    } else {
        $('div#' + assignEntity + '-search-results').empty()
    }
}

$('#assign-agent').click(function() {
    $('div#agent-search').show()
    $('#assign-agent-search').focus()
})

$('i#cancel-assign-agent').click(function() {
    $('#assign-agent-search').val('').trigger('change')
    $('div#agent-search').hide()
    $('div#agent-search-results').empty()
})

var assignAgent = function(objectId, userId, propertyContact) {
    $.ajax({
        url: '/crm/' + propertyContact + '/' + objectId + '/asignar_agente' + (userId ? ('/' + userId) : ''),
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
//Assign agent logic

//Search logic
setUpGeographyHierarchies('contact-search', false)

//select2 set up
$('#search-modal select#type').select2({language: {'noResults': function() {return 'No hay datos'}}})
$('#search-modal').on('shown.bs.modal', function() {
    state = $('#search-modal select#state').val()
    city = $('#search-modal select#city').val()
    neighborhood = $('#search-modal select#neighborhood').val()
    resetStateDropDown(true)
    $('#search-modal select#state').val(state ? state : '0').trigger('change')
    resetCityDropDown(true)
    $('#search-modal select#city').val(city ? city : '0').trigger('change')
    resetNeighborhoodDropDown(true)
    $('#search-modal select#neighborhood').val(neighborhood ? neighborhood : '0').trigger('change')
    $('.select2-container').css('width', '100%')

    $('#search-modal a.search-section-show-hide i').addClass('fa-plus')
    $('#search-modal a.search-section-show-hide i').removeClass('fa-minus')
    $('#search-modal .section-row').hide()
})
//select2 set up

//TouchSpin set up
$('#search-modal input#sale-price-from, #search-modal input#sale-price-to, #search-modal input#rent-price-from, #search-modal input#rent-price-to').TouchSpin({
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

$('#search-modal input#sale-price-usd-from, #search-modal input#sale-price-usd-to, #search-modal input#rent-price-usd-from, #search-modal input#rent-price-usd-to').TouchSpin({
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

$('#search-modal .touch-spin-small').TouchSpin({
    min: 0,
    max: 1000000000,
    decimals: 0,
    step: 1,
    boostat: 5,
    maxboostedstep: 10000,
    mousewheel: false,
    verticalbuttons: true
})

var enableDisableTouchSpin = function($elem, enabled) {
    $elem.prop('disabled', !enabled)
    $elem.parent().find('#search-modal span.input-group-btn button').prop('disabled', !enabled)
}
//TouchSpin set up

$('#search-modal a.search-section-show-hide').click(function() {
    thisElem = this
    if ($(thisElem).find('i').hasClass('fa-minus')) {
        $(thisElem).find('i').removeClass('fa-minus')
        $(thisElem).find('i').addClass('fa-plus')
        $(thisElem).parents('div.search-section').find('.section-row').hide()
    } else {
        $(thisElem).find('i').removeClass('fa-plus')
        $(thisElem).find('i').addClass('fa-minus')
        $(thisElem).parents('div.search-section').find('.section-row').show()
    }
})

var contactSearchParametersChanged = false
$('#search-modal #search-parameters-box input.form-control,input[type=radio],select').change(function() {
    contactSearchParametersChanged = true
})
var showSearchDetails = function (thisElem, keepValues, showButtons, showCommentaryBox, showResultsBox, title) {
    searchId = $(thisElem).attr('search-id')
    $('#search-results-box .box-body').empty()

    if (!keepValues) {
        $('#search-modal select#type').val([]).trigger('change')
        $('#search-modal input[value=all]').prop('checked', true)
        resetDropDown($('#search-modal select#country'), $.map(geographyHierarchy.countries, function(c) {return {id: c.id, text: c.name}}), 'País', true)
        $('#search-modal input[type=text], #search-modal textarea').val(undefined)
    }

    if (searchId) {
        $.ajax({
            url: '/crm/contacto/' + $('form#contact-info').attr('contact-id') + '/busqueda/' + searchId,
            method: 'GET',
            dataType: 'json',
            success: function(r) {
                $('#search-modal-title').text(r.title + ' - ' + r.date)
                $('#search-modal textarea#commentary').val(r.commentary)
                $.each(r.elements, function(k, e) {
                    values = JSON.parse(e.values)
                    //Attributes
                    if (e.attribute == 'type_id') {$('#search-modal select#type').val(values).trigger('change')}
                    if (e.attribute == 'status_id') {$('#search-modal input#status[value=' + (values == 0 ? 'all' : 'available') + ']').prop('checked', true)}
                    if (e.attribute == 'expenses') {
                        if (e.operation == 'range') {
                            $('#search-modal input#expenses-from').val(values[0] ? values[0] : undefined)
                            $('#search-modal input#expenses-to').val(values[1])
                        } else {
                            $('#search-modal input#expenses-from').val(values)
                        }
                    }
                    if (e.attribute == 'rooms') {
                        if (e.operation == 'range') {
                            $('#search-modal input#rooms-from').val(values[0] ? values[0] : undefined)
                            $('#search-modal input#rooms-to').val(values[1])
                        } else {
                            $('#search-modal input#rooms-from').val(values)
                        }
                    }
                    if (e.attribute == 'bathrooms') {
                        if (e.operation == 'range') {
                            $('#search-modal input#bathrooms-from').val(values[0] ? values[0] : undefined)
                            $('#search-modal input#bathrooms-to').val(values[1])
                        } else {
                            $('#search-modal input#bathrooms-from').val(values)
                        }
                    }
                    if (e.attribute == 'surface') {
                        if (e.operation == 'range') {
                            $('#search-modal input#surface-from').val(values[0] ? values[0] : undefined)
                            $('#search-modal input#surface-to').val(values[1])
                        } else {
                            $('#search-modal input#surface-from').val(values)
                        }
                    }
                    if (e.attribute == 'covered-surface') {
                        if (e.operation == 'range') {
                            $('#search-modal input#covered_surface-from').val(values[0] ? values[0] : undefined)
                            $('#search-modal input#covered_surface-to').val(values[1])
                        } else {
                            $('#search-modal input#covered_surface-from').val(values)
                        }
                    }
                    if (e.attribute == 'orientation') {$('#search-modal input#orientation').val(values)}
                    if (e.attribute == 'age') {
                        if (e.operation == 'range') {
                            $('#search-modal input#age-from').val(values[0] ? values[0] : undefined)
                            $('#search-modal input#age-to').val(values[1])
                        } else {
                            $('#search-modal input#age-from').val(values)
                        }
                    }
                    if (e.attribute == 'garages') {
                        if (e.operation == 'range') {
                            $('#search-modal input#garages-from').val(values[0] ? values[0] : undefined)
                            $('#search-modal input#garages-to').val(values[1])
                        } else {
                            $('#search-modal input#garages-from').val(values)
                        }
                    }
                    //Sale
                    if (e.attribute == 'for_sale') {$('#search-modal input#for-sale[value=' + (values ? 'yes' : 'no') + ']').prop('checked', true)}
                    if (e.attribute == 'sale_price') {
                        if (e.operation == 'range') {
                            $('#search-modal input#sale-price-from').val(values[0] ? values[0] : undefined)
                            $('#search-modal input#sale-price-to').val(values[1])
                        } else {
                            $('#search-modal input#sale-price-from').val(values)
                        }
                    }
                    if (e.attribute == 'sale_price_usd') {
                        if (e.operation == 'range') {
                            $('#search-modal input#sale-price-usd-from').val(values[0] ? values[0] : undefined)
                            $('#search-modal input#sale-price-usd-to').val(values[1])
                        } else {
                            $('#search-modal input#sale-price-usd-from').val(values)
                        }
                    }
                    //Rent
                    if (e.attribute == 'for_rent') {$('#search-modal input#for-rent[value=' + (values ? 'yes' : 'no') + ']').prop('checked', true)}
                    if (e.attribute == 'rent_price') {
                        if (e.operation == 'range') {
                            $('#search-modal input#rent-price-from').val(values[0] ? values[0] : undefined)
                            $('#search-modal input#rent-price-to').val(values[1])
                        } else {
                            $('#search-modal input#rent-price-from').val(values)
                        }
                    }
                    if (e.attribute == 'rent_price_usd') {
                        if (e.operation == 'range') {
                            $('#search-modal input#rent-price-usd-from').val(values[0] ? values[0] : undefined)
                            $('#search-modal input#rent-price-usd-to').val(values[1])
                        } else {
                            $('#search-modal input#rent-price-usd-from').val(values)
                        }
                    }
                    //Location
                    if (e.attribute == 'city__state__country_id') {$('#search-modal select#country').val(values).trigger('change')}
                    if (e.attribute == 'city__state_id') {$('#search-modal select#state').val(values).trigger('change')}
                    if (e.attribute == 'city_id') {$('#search-modal select#city').val(values).trigger('change')}
                    if (e.attribute == 'neighborhood_id') {$('#search-modal select#neighborhood').val(values).trigger('change')}
                    if (e.attribute == 'street') {$('#search-modal input#street').val(values)}
                    if (e.attribute == 'number') {$('#search-modal input#number').val(values)}
                    if (e.attribute == 'floor') {$('#search-modal input#floor').val(values)}
                    if (e.attribute == 'apartment') {$('#search-modal input#apartment').val(values)}
                    if (e.attribute == 'intersecting_street_1' || e.attribute == 'intersecting_street_2') {$('#search-modal input#intersecting-streets').val(values)}
                    if (e.attribute == 'anonymous_address') {$('#search-modal input#anonymous-address').val(values)}
                    if (e.attribute == 'description') {$('#search-modal input#description').val(values)}
                })
                $('#remove-search').show()
                $('#search-modal').modal('show')
                $('#search-modal').attr('search-id', searchId)
                if ($('#search-results-box').hasClass('collapsed-box')) {$('#search-results-box button[data-widget=collapse]').trigger('click')}
                $('#search-modal textarea#commentary').unbind('focusout')
                $('#search-modal textarea#commentary').focusout(function() {searchCommentarySave(this)})
                contactSearchParametersChanged = false
                executeSearch(true, contactSearchParametersChanged)
            }
        })
    } else {
        $('#search-modal textarea#commentary').unbind('focusout')
        $('#remove-search').hide()
        $('#search-modal').removeAttr('search-id')
        $('#search-modal-title').text(title)
        $('#search-modal .modal-body').animate({scrollTop: $('#search-parameters-box').parent().position().top})
        if ($('#search-parameters-box').hasClass('collapsed-box')) {$('#search-parameters-box button[data-widget=collapse]').trigger('click')}
        if (!$('#search-results-box').hasClass('collapsed-box')) {$('#search-results-box button[data-widget=collapse]').trigger('click')}
        $('#search-modal').modal('show')
    }

    if (!showButtons) {
        $('#search-modal button').hide()
        $('#search-modal button.close, #search-modal button#back').show()
    }

    if (showCommentaryBox) {
        $('#search-modal div#search-commentary-box').parent().show()
    } else {
        $('#search-modal div#search-commentary-box').parent().hide()
    }

    if (showResultsBox) {
        $('#search-modal div#search-results-box').parent().show()
    } else {
        $('#search-modal div#search-results-box').parent().hide()
    }
}
//Search logic