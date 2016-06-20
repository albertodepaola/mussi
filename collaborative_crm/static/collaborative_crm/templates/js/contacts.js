// Contacts data loading
var loadContactsData = function(searchTerm) {
    parameters = {}
    if ($('div#contacts-page').hasClass('my-contacts')) {
        parameters['my_contacts'] = true
    }
    if (searchTerm) {
        parameters['search_term'] = searchTerm
    }
    $('.content-wrapper').animate({scrollTop: 0})
    if ($('div#contacts img.ajax-wait').length == 0) {$('div#contacts').prepend($('<div/>', {style: 'heigth: 150px;'}).append($('<img/>', {class: 'ajax-wait', src: '/static/collaborative_crm/images/misc/ajax.gif', style: 'height: 150px; width: 150px; margin: auto; display: block;'})))}
    $.ajax({
        url: '/crm/buscar_contactos',
        method: 'POST',
        data: JSON.stringify(parameters),
        dataType: 'html',
        success: function(r) {
            $('div#contacts')
                .empty()
                .append($('<div/>', {style: 'heigth: 150px;'}).append($('<img/>', {class: 'ajax-wait', src: '/static/collaborative_crm/images/misc/ajax.gif', style: 'height: 150px; width: 150px; margin: auto; display: block;'})))
                .append(r)
            $('img.ajax-wait').parent().remove()

            // Contact details logic
            $('a.show-contact-details').click(function() {showContactDetailsModal($(this).attr('contact-id'))})
            // Contact details logic
        }
    })
}
$(function() {loadContactsData()})
// Contacts data loading

// Filters logic
$('input#search-contacts').change(function() {loadContactsData($(this).val())}).keypress(function(e) {if (e.keyCode == 13) {loadContactsData($(this).val())}}).keyup($.throttle(750, function() {loadContactsData($(this).val())}))
$('a#reestablish-search').click(function() {$('input#search-contacts').val('').trigger('change')})
// Filters logic