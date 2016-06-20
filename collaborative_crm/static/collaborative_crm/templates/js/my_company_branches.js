//geography hierarchy logic
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

var resetStateDropDown = function(setToZero) {resetDropDown($('select#state'), $.map(geographyHierarchy.states.filter(function(s) {return s.country_id == $('select#country').val()}), function(s) {return {id: s.id, text: s.name}}), 'Provincia/Estado', setToZero)}
var resetCityDropDown = function(setToZero) {resetDropDown($('select#city'), $.map(geographyHierarchy.cities.filter(function(c) {return c.state_id == $('select#state').val()}), function(c) {return {id: c.id, text: c.name}}), 'Ciudad', setToZero)}

var geographyHierarchy
$.ajax(
    {
        url: '/crm/geografia',
        method: 'GET',
        dataType: 'json',
        success: function(data) {
            geographyHierarchy = data
            $('select#type').select2({language: {'noResults': function() {return 'No hay datos'}}})
            $('select#status').select2({language: {'noResults': function() {return 'No hay datos'}}})
            $('select#country').select2({language: {'noResults': function() {return 'No hay datos'}}})
            resetStateDropDown()
            $('select#state').val($('select#state').attr('value')).trigger('change')
            resetCityDropDown()
            $('select#city').val($('select#city').attr('value')).trigger('change')

            $('select#country').change(function() {
                    resetStateDropDown(true)
                    resetCityDropDown(true)
                }
            )

            $('select#state').change(function() {
                    resetCityDropDown(true)
                }
            )
        }
    }
)

$(function() {
    $('select#country').val($('select#country').attr('value')).trigger('change')
    $('select#state').val($('select#state').attr('value')).trigger('change')
    $('select#city').val($('select#city').attr('value')).trigger('change')
})
//geography hierarchy logic

//Get branch data logic
var updateBranchForm = function(branchData) {
    branchData = branchData ? branchData : {}
    $('h3#branch-box-title').text(branchData.name ? branchData.name : 'Nueva Sucursal')
    $('input#code').val(branchData.code)
    $('input#name').val(branchData.name)
    $('select#country').val(branchData.country_id ? branchData.country_id : 1).trigger('change')
    $('select#state').val(branchData.state_id).trigger('change')
    $('select#city').val(branchData.city_id).trigger('change')
    $('input#address').val(branchData.address)
    $('textarea#description').val(branchData.description)
}

$('select#branch').change(function() {
    var branchId = parseInt($(this).val())
    $('form#branch-info').attr('action', '/crm/empresa/' + $('form#branch-info').attr('company-id') + '/sucursales/' + branchId + '/actualizar_datos')
    var branchData

    if (branchId) {
        $('button#remove-branch').show()
        $.ajax({
            url: '/crm/empresa/' + $('form#branch-info').attr('company-id') + '/sucursales/' + branchId + '/detalles',
            method: 'GET',
            dataType: 'json',
            success: function(r) {
                updateBranchForm(r)
            }
        })
    } else {
        $('button#remove-branch').hide()
        updateBranchForm()
    }
})
//Get branch data logic

//Remove logic
$('button#remove-branch').click(function() {$('#remove-branch-modal').modal('show')})
$('button#confirm-remove').click(function() {
    $.ajax({
        url: '/crm/empresa/' + $('form#branch-info').attr('company-id') + '/sucursales/' + $('select#branch').val() + '/eliminar',
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