// News data loading
var newsSetUpSlimScroll = function() {
    $('.news-box-body').slimScroll({destroy: true})
    setTimeout(function() {
        $('.news-box-body').slimScroll({height: (parseInt($('.news-box-body').css('width')) / 2.5) + 'px'})
        $('.news-box-body').scroll(function() {
            var thisElem = this
            $(thisElem).find('img').parent().css('top', $(thisElem).scrollTop())
        })
    }, 300)
}

var loadNewsData = function(filters) {
    $('.content-wrapper').animate({scrollTop: 0})
    if ($('div#news img.ajax-wait').length == 0) {$('div#news').prepend($('<div/>', {style: 'heigth: 150px;'}).append($('<img/>', {class: 'ajax-wait', src: '/static/collaborative_crm/images/misc/ajax.gif', style: 'height: 150px; width: 150px; margin: auto; display: block;'})))}
    $.ajax({
        url: '/crm/noticias_datos',
        method: 'POST',
        data: JSON.stringify(filters),
        dataType: 'html',
        success: function(r) {
            $('div#news')
                .empty()
                .append($('<div/>', {style: 'heigth: 150px;'}).append($('<img/>', {class: 'ajax-wait', src: '/static/collaborative_crm/images/misc/ajax.gif', style: 'height: 150px; width: 150px; margin: auto; display: block;'})))
                .append(r)
            $('img.ajax-wait').parent().remove()

            //slimScroll set up
            newsSetUpSlimScroll()
            $(window).resize(newsSetUpSlimScroll)
            //slimScroll set up

            //History logic
            $.each($('.news-box-body a'), function(k, a) {
                setUpHistoryLogic($(a), $(a).parents('.box').hasClass('property') ? 'propiedad' : 'contacto', $(a).attr('property-id') ? $(a).attr('property-id') : $(a).attr('contact-id'))
            })
            //History logic

            // Property details logic
            $('.property .news-box-header a').click(function() {showPropertyDetailsModal($(this).attr('property-id'))})
            // Property details logic

            // Contact details logic
            $('.contact .news-box-header a').click(function() {showContactDetailsModal($(this).attr('contact-id'))})
            // Contact details logic
        }
    })
}
$(loadNewsData)
// News data loading

// Filters logic
$('form#news-filters .filter').change(function () {
    var value = $(this).val()
    if (value && value != 'selected-users') {
        loadNewsData({
            entities: $('input#entities:checked').val(),
            users: $('input#users:checked').val() == 'me' ? 'me' : ($('input#users:checked').val() == 'selected-users' ? $('select#selected-users').val() : undefined),
            users_in_charge: $('input#users-in-charge:checked').val() == 'me' ? 'me' : ($('input#users-in-charge:checked').val() == 'selected-users' ? $('select#selected-users-in-charge').val() : undefined),
            week_from: parseInt($('select#week-from').val()),
            week_to: parseInt($('select#week-to').val())
        })
    }
})

$('.filter-select2').select2({language: {'noResults': function() {return 'No hay datos'}}})
$('.select2-container').css('width', '100%')
$('.filter-select2').parents('div.radio-col').find('.select2-container').hide()

$('input[type=radio]').change(function() {
    var thisElem = this
    if ($(thisElem).val() == 'selected-users') {
        $(thisElem).parents('div.radio-col').find('.select2-container').show()
    } else {
        $(thisElem).parents('div.radio-col').find('select').val([]).trigger('change')
        $(thisElem).parents('div.radio-col').find('.select2-container').hide()
    }
})
// Filters logic