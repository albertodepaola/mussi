// Properties data loading
var propertiesSetUpBoxes = function() {
    //$('.search-result-box-body').slimScroll({destroy: true})
    setTimeout(function() {
        //$('.search-result-box-body').slimScroll({height: (parseInt($('.search-result-box-body').css('width')) / 2.5) + 'px'})
        $('.search-result-box-body').css('height', (parseInt($('.search-result-box-body').css('width')) / 2) + 'px')
    }, 300)
}

var loadPropertiesData = function(filters) {
    filters = (!filters ? {parameters: []} : filters)
    if ($('div#properties-page').hasClass('my-properties')) {
        filters['parameters'].push({attribute: 'user_id', operation: 'exact', values: 'me', boolean: false})
    }
    $('.content-wrapper').animate({scrollTop: 0})
    if ($('div#properties img.ajax-wait').length == 0) {$('div#properties').prepend($('<div/>', {style: 'heigth: 150px;'}).append($('<img/>', {class: 'ajax-wait', src: '/static/collaborative_crm/images/misc/ajax.gif', style: 'height: 150px; width: 150px; margin: auto; display: block;'})))}
    $.ajax({
        url: '/crm/buscar_propiedades',
        method: 'POST',
        data: JSON.stringify(filters),
        dataType: 'html',
        success: function(r) {
            $('div#properties')
                .empty()
                .append($('<div/>', {style: 'heigth: 150px;'}).append($('<img/>', {class: 'ajax-wait', src: '/static/collaborative_crm/images/misc/ajax.gif', style: 'height: 150px; width: 150px; margin: auto; display: block;'})))
                .append(r)
            $('img.ajax-wait').parent().remove()

            propertiesSetUpBoxes()
            $(window).resize(propertiesSetUpBoxes)

            $('button.property-file-button').click(function() {
                var thisElem = this
                showFileModal($(thisElem).attr('property-id'))
            })

            // Property details logic
            $('a.search-result-show-property-details').click(function() {showPropertyDetailsModal($(this).attr('property-id'))})
            // Property details logic
        }
    })
}
$(function() {loadPropertiesData()})
// Properties data loading

// Filters logic
var advancedFilters = false
filterOnChange = function() {
    if (!advancedFilters) {
        $('#search-modal input#status[value=' + $('form#search-properties input#status:checked').val() + ']').prop('checked', true)
        $('#search-modal select#type').val($('form#search-properties select#type').val())

        if ($('form#search-properties input#sale-rent:checked').val() != 'for-sale') {
            $('#search-modal input#sale-price-from').val(undefined)
            $('#search-modal input#sale-price-to').val(undefined)
            $('#search-modal input#sale-price-usd-from').val(undefined)
            $('#search-modal input#sale-price-usd-to').val(undefined)
        } else if ($('form#search-properties input#sale-rent:checked').val() != 'for-rent') {
            $('#search-modal input#rent-price-from').val(undefined)
            $('#search-modal input#rent-price-to').val(undefined)
            $('#search-modal input#rent-price-usd-from').val(undefined)
            $('#search-modal input#rent-price-usd-to').val(undefined)
        }

        if ($('form#search-properties input#sale-rent:checked').val() == 'for-sale') {
            $('#search-modal input#sale-price-from').val($('form#search-properties input#price-from').val())
            $('#search-modal input#sale-price-to').val($('form#search-properties input#price-to').val())
            $('#search-modal input#sale-price-usd-from').val($('form#search-properties input#price-usd-from').val())
            $('#search-modal input#sale-price-usd-to').val($('form#search-properties input#price-usd-to').val())
        } else if ($('form#search-properties input#sale-rent:checked').val() == 'for-rent') {
            $('#search-modal input#rent-price-from').val($('form#search-properties input#price-from').val())
            $('#search-modal input#rent-price-to').val($('form#search-properties input#price-to').val())
            $('#search-modal input#rent-price-usd-from').val($('form#search-properties input#price-usd-from').val())
            $('#search-modal input#rent-price-usd-to').val($('form#search-properties input#price-usd-to').val())
        }

        if ($('#search-modal input#for-sale:checked').val() != 'no') {$('#search-modal input#for-sale[value=' + ($('form#search-properties input#sale-rent:checked').val() == 'for-sale' ? 'yes' : 'all') + ']').prop('checked', true)}
        if ($('#search-modal input#for-rent:checked').val() != 'no') {$('#search-modal input#for-rent[value=' + ($('form#search-properties input#sale-rent:checked').val() == 'for-rent' ? 'yes' : 'all') + ']').prop('checked', true)}
    }

    var filters = {parameters: []}

    if (!advancedFilters) {
        filters['parameters'].push({attribute: 'status_id', operation: 'exact', values: $('form#search-properties input#status:checked').val() == 'available' ? 1 : 0, boolean: false})
        filters['parameters'].push({attribute: 'type_id', operation: 'in', values: $('form#search-properties select#type').val(), boolean: false})
        filters['parameters'].push({attribute: 'city_id', operation: 'in', values: $('form#search-properties select#neighborhood').val() ? $.map($('form#search-properties select#neighborhood').val().filter(function(e) {return e.indexOf('city') > -1}), function(e) {return parseInt(e.split('-')[1])}) : null, boolean: false})
        filters['parameters'].push({attribute: 'neighborhood_id', operation: 'in', values: $('form#search-properties select#neighborhood').val() ? $.map($('form#search-properties select#neighborhood').val().filter(function(e) {return e.indexOf('neighborhood') > -1}), function(e) {return parseInt(e.split('-')[1])}) : null, boolean: false})
        filters['parameters'].push({attribute: 'for_sale', operation: 'exact', values: $('form#search-properties input#sale-rent:checked').val() == 'for-sale' ? 'yes' : undefined, boolean: true}),
        filters['parameters'].push({attribute: 'for_rent', operation: 'exact', values: $('form#search-properties input#sale-rent:checked').val() == 'for-rent' ? 'yes' : undefined, boolean: true}),
        saleRentAttr = $('form#search-properties input#sale-rent:checked').val() == 'for-sale' ? 'sale_price' : ($('form#search-properties input#sale-rent:checked').val() == 'for-rent' ? 'rent_price' : undefined)
        if (saleRentAttr) {
            filters['parameters'].push({attribute: saleRentAttr, operation: (parseInt($('form#search-properties #price-to').val())) ? 'range' : 'gte', values: (parseInt($('form#search-properties #price-to').val())) ? [parseInt($('form#search-properties #price-from').val()) ? parseInt($('form#search-properties #price-from').val()) : 0, parseInt($('form#search-properties #price-to').val())] : (parseInt($('form#search-properties #price-from').val()) ? parseInt($('form#search-properties #price-from').val()) : 0), boolean: false})
            filters['parameters'].push({attribute: saleRentAttr + '_usd', operation: (parseInt($('form#search-properties #price-usd-to').val())) ? 'range' : 'gte', values: (parseInt($('form#search-properties #price-usd-to').val())) ? [parseInt($('form#search-properties #price-usd-from').val()) ? parseInt($('form#search-properties #price-usd-from').val()) : 0, parseInt($('form#search-properties #price-usd-to').val())] : (parseInt($('form#search-properties #price-usd-from').val()) ? parseInt($('form#search-properties #price-usd-from').val()) : 0), boolean: false})
        }
    } else {
        filters['parameters'] = [
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
        ]
    }

    loadPropertiesData(filters)
}

$('#search-modal').on('shown.bs.modal', function() {
    $('#search-modal select#type').trigger('change')
    $('#search-modal select#neighborhood').trigger('change')
}).on('hidden.bs.modal', function() {
    filterOnChange()
})

var enableDisableTouchSpin = function($elem, enabled) {
    $elem.prop('disabled', !enabled)
    $elem.parent().find('span.input-group-btn button').prop('disabled', !enabled)
}

$('form#search-properties #sale-rent').change(function() {
    $('input.filter-price').val(undefined)
    $('input.filter-price-usd').val(undefined)
    if ($('form#search-properties #sale-rent:checked').val() != 'all') {
        enableDisableTouchSpin($('input.filter-price'), true)
        enableDisableTouchSpin($('input.filter-price-usd'), true)
    } else {
        enableDisableTouchSpin($('input.filter-price'), false)
        enableDisableTouchSpin($('input.filter-price-usd'), false)
    }
})

enableDisableTouchSpin($('input.filter-price'), false)
enableDisableTouchSpin($('input.filter-price-usd'), false)

$('form#search-properties .filter').change(filterOnChange)
$('form#search-properties .filter-touchspin').change($.throttle(750, filterOnChange))

$('.filter-select2').select2({
    language: {
        noResults: function() {return 'No hay datos'},
        inputTooShort: function(args) {return 'Mínimo ' + args.minimum + ' caracteres para buscar'},
        searching: function() {return 'Buscando...'}
    },
    placeholder: {value: undefined, text: 'Escriba para buscar'},
  ajax: {
    url: function (params) {
      return '/crm/geografia/buscar/ciudades-barrios/' + params.term;
    },
    dataType: 'json',
    delay: 250,
    processResults: function (data, params) {
      return {
        results: $.map(data, function(e) {return {id: e.type + '-' + e.id, text: e.full_name}}),
      }
    },
    cache: true
  },
  minimumInputLength: 3
})
$('.select2-container').css('width', '100%')

$('input.filter-price').TouchSpin({
    min: 0,
    max: 1000000000,
    decimals: 0,
    step: 1,
    prefix: '$',
    postfix: '',
    boostat: 5,
    maxboostedstep: 10000,
    mousewheel: false
})

$('input.filter-price-usd').TouchSpin({
    min: 0,
    max: 1000000000,
    decimals: 0,
    step: 1,
    prefix: 'US$',
    postfix: '',
    boostat: 5,
    maxboostedstep: 10000,
    mousewheel: false
})

$('#show-advanced-filters').click(function() {
    var thisElem = this
    if ($(thisElem).parent().find('span.label.label-danger').length == 0) {
        $(thisElem).after($('<span/>', {class: 'label label-danger', text: 'Filtros avanzados aplicados'})).after('&nbsp;&nbsp;')
    }
    advancedFilters = true
    $('form#search-properties').remove()
    showSearchDetails(this, true, false, false, false, 'Filtros avanzados')
})

$('label.search').click(function() {
    $('div#search-parameters').toggle()
    if ($('div#search-parameters').css('display') == 'block') {
        $('i#search-properties-show-hide').removeClass('fa-plus').addClass('fa-minus')
    } else {
        $('i#search-properties-show-hide').removeClass('fa-minus').addClass('fa-plus')
    }
})
// Filters logic