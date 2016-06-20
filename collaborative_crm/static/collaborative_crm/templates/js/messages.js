//Slim scroll logic
var slimScrollAnimatedScrollToFinish = function($slimScroll, animateTime) {
    animateTime = animateTime ? animateTime : 1000
    $slimScroll.animate({scrollTop: $slimScroll.prop('scrollHeight')}, animateTime)
    $slimScroll.slimScroll({scrollTo: $slimScroll.prop('scrollHeight')})
}

var setUpSlimScroll = function() {
    $('.box-body.chat-box, .box-body.conversations').slimScroll({destroy: true})
    setTimeout(function() {
        $('.box-body.chat-box, .box-body.conversations').slimScroll({
            height: parseInt($('.content-wrapper').css('height')) - parseInt($('.main-footer').css('height')) - parseInt($('.box-header').css('height')) - parseInt($('.input-group.send-message').css('height')) - 15
        })
        slimScrollAnimatedScrollToFinish($('.box-body.chat-box'))
    }, 300)
}

$(window).resize(setUpSlimScroll)
//Slim scroll logic

//Add/select conversation logic
$('#add-conversation-modal select#users').select2({language: {'noResults': function() {return 'No hay datos'}}})
$('#add-conversation-modal select#users').change(function() {
    $('button#create-conversation').prop('disabled', !$(this).val())
})

$('#add-conversation-modal').on('shown.bs.modal', function() {
    $('.select2-container').css('width', '100%')
})

$('a#add-conversation').click(function() {
    $('#add-conversation-modal').modal('show')
})

var selectConversation = function() {
    var thisElem = this
    $('.conversations div.item.selected').removeClass('selected')
    $(thisElem).parents('div.item').addClass('selected')
    $(thisElem).find('small').empty().append($('<i/>', {class: 'fa fa-weixin'})).append(' 0').css('display', 'none')
    if ($(thisElem).attr('conversation-id') != $('#chat-box').attr('conversation-id')) {

        $.ajax({
            url: '/crm/conversacion/' + $(thisElem).attr('conversation-id') + '/mensajes/leer',
            method: 'GET',
            dataType: 'html',
            success: function(r) {
                $('#chat-box .box-body').empty().append(r)
                $('#chat-box .box-title').text($($(thisElem).contents()[$(thisElem).contents().length - 1]).text())
                $('#chat-box').attr('conversation-id', $(thisElem).attr('conversation-id'))
                setUpSlimScroll()
            }
        })
    }
}

$('.conversations a.name').click(selectConversation)
$(function() {
    $('.conversations div.item.selected a.name').trigger('click')
})

$('button#create-conversation').click(function() {
    $.ajax({
        url: '/crm/crear_conversacion',
        method: 'POST',
        data: JSON.stringify({'title': $('#add-conversation-modal input#title').val(), 'users': $('#add-conversation-modal select#users').val()}),
        dataType: 'json',
        success: function(r) {
            if (r.status == 'Ok') {
                $a = $('<a/>', {class: 'name', 'conversation-id': r.conversation.id})
                        .append($('<small/>', {class: 'text-muted pull-right', style: 'display: none;'})
                            .append($('<i/>', {class: 'fa fa-weixin'}))
                            .append(' 0'))
                        .append(r.conversation.title)
                        .click(selectConversation)

                $conversationDiv = $('<div/>', {class: 'item ' + ($('.conversations div.item').length ? 'not-last' : 'last')})
                                        .append($('<img/>', {alt: 'user image', class: 'chat-primary', src: '/static/collaborative_crm/images/misc/conversation.png'}))
                                        .append($('<p/>', {class: 'message'})
                                            .append($a)
                                            .append($('<small/>', {text: r.conversation.users_names_list})))

                $('.conversations').prepend($conversationDiv)
                $('#add-conversation-modal').modal('hide')
                $a.trigger('click')
                $('#add-conversation-modal input#title').val('')
                $('#add-conversation-modal select#users').val([]).trigger('change')
            } else {
                alert(r.exception_class + ' - ' + r.exception_message)
            }
        }
    })
})
//Add/select conversation logic

// Send message logic
var addChatItem = function(from, timestamp, content) {
    $('.chat-box div.item.last').removeClass('last').addClass('not-last')

    $chatDiv = $('<div/>', {class: 'item last'})
                .append($('<img/>', {alt: 'user image', class: 'online', src: '/static/collaborative_crm/images/misc/default_user.png'}))
                .append($('<p/>', {class: 'message'})
                    .append($('<a/>', {class: 'name'})
                        .append($('<small/>', {class: 'text-muted pull-right'})
                            .append($('<i/>', {class: 'fa fa-clock-o'}))
                            .append(' ' + timestamp))
                        .append(from))
                    .append($('<small/>', {text: content})))

    $('.box-body.chat-box').append($chatDiv)

    slimScrollAnimatedScrollToFinish($('.box-body.chat-box'))
}

var sendMessage = function() {
    if ($('input.send-message').val()) {
        $.ajax({
            url: '/crm/conversacion/' + $('#chat-box').attr('conversation-id') + '/enviar_mensaje',
            method: 'POST',
            data: $('input.send-message').val(),
            dataType: 'json',
            success: function(r) {
                if (r.status == 'Ok') {
                    addChatItem('Yo', r.message.timestamp, r.message.content)
                    $('input.send-message').val('')
                } else {
                    alert(r.exception_class + ' - ' + r.exception_message)
                }
            }
        })
    }
}

$('input.send-message').keyup(function(e) {if (e.keyCode == 13) {sendMessage()}})
$('button.send-message').click(sendMessage)
// Send message logic

//Override action when message is received
var messageAction = function(data) {
    var currentlySelectedConv = parseInt($('#chat-box').attr('conversation-id'))
    if (data.conversation_id == currentlySelectedConv) {
        if (data.from_id != myUserId) {
            addChatItem(data.from, data.timestamp, data.content)
        }
    } else {
        messageDefaultAction(data)
    }
    $('.box-body.conversations').replaceWith(data.conversations_html)
    $('.conversations div.item.selected').removeClass('selected')
    $('.conversations a.name[conversation-id=' + currentlySelectedConv + ']').parents('div.item').addClass('selected')
    $('.conversations a.name').click(selectConversation)
    $('.conversations a.name[conversation-id=' + currentlySelectedConv + ']').find('small.unred-messages-count').hide()

}
//Override action when message is received