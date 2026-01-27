let input_message = $('#input-message')
// let message_body = $('.msg_card_body')
let send_message_form = $('#send-message-form')
const USER_ID = $('#logged-in-user').val()

let loc = window.location
let wsStart = 'ws://'

if (loc.protocol === 'https') {
    wsStart = 'wss://'
}
let endpoint = wsStart + loc.host + loc.pathname

var socket = new WebSocket(endpoint)

socket.onopen = async function (e) {
    console.log('open', e)
    send_message_form.on('submit', function (e) {
        e.preventDefault()
        let message = input_message.val()
        let send_to = get_active_other_user_id()
        let thread_id = get_active_thread_id()

        let data = {
            'message': message,
            'sent_by': USER_ID,
            'send_to': send_to,
            'thread_id': thread_id
        }
        data = JSON.stringify(data)
        socket.send(data)
        $(this)[0].reset()
    })
}

socket.onmessage = async function (e) {
    console.log('message', e)
    let data = JSON.parse(e.data)
    let message = data['message']
    let sent_by_id = data['sent_by']
    let thread_id = data['thread_id']
    newMessage(message, sent_by_id, thread_id)
}

socket.onerror = async function (e) {
    console.log('error', e)
}

socket.onclose = async function (e) {
    console.log('close', e)
}

function newMessage(message, sent_by_id, thread_id) {
    if ($.trim(message) === '') {
        return false;
    }
    let message_element;
    let chat_id = 'chat_' + thread_id
    if (sent_by_id == USER_ID) {
        message_element = `
        <ul class="m-b-0">
          <li class="clearfix">
            <div class="message other-message float-right">
              ${message}
            </div>
          </li>
        </ul>
	    `
    } else {
        message_element = `
        <ul class="m-b-0">
          <li class="clearfix">
            <div class="message my-message">
              ${message}
            </div>
          </li>
        </ul>
        `
    }

    let message_body = $('.messages-wrapper[chat-id="' + chat_id + '"] .chat-history')
    message_body.append($(message_element))
    message_body.animate({
        scrollTop: message_body[0].scrollHeight
    }, 100);
    input_message.val(null);
}


$('.contact-li').on('click', function () {
    $('.contact-li.active').removeClass('active');
    $(this).addClass('active')

    // message wrappers
    let chat_id = $(this).attr('chat-id')

    $('.messages-wrapper.is_active').removeClass('is_active')
    $('.messages-wrapper[chat-id="' + chat_id + '"]').addClass('is_active')
    // when switch btw chats
    scrollToBottom($('.messages-wrapper.is_active .chat-history'));
})

// Auto-activate chat if thread_id is in URL
$(document).ready(function() {
    const params = new URLSearchParams(window.location.search);
    const threadId = params.get('thread_id');
    if (threadId) {
        let chat_id = 'chat_' + threadId;
        // Activate the contact in the list
        $('.contact-li').removeClass('active');
        $('.contact-li[chat-id="' + chat_id + '"]').addClass('active');
        // Activate the chat window
        $('.messages-wrapper').removeClass('is_active');
        $('.messages-wrapper[chat-id="' + chat_id + '"]').addClass('is_active');
        scrollToBottom($('.messages-wrapper[chat-id="' + chat_id + '"] .chat-history'));
    }

    // Paperclip (file) button functionality
    $('#file-input').on('change', function(e) {
        handleFileUpload(e.target.files[0]);
    });
    // Gallery button functionality
    $('#gallery-input').on('change', function(e) {
        handleImageUpload(e.target.files[0]);
    });
});



function handleImageUpload(file) {
        if (!file) return;
        let reader = new FileReader();
        reader.onload = function(e) {
                let imageData = e.target.result;
                let send_to = get_active_other_user_id();
                let thread_id = get_active_thread_id();
                // Image is clickable to expand, and has a download button
                let messageHtml = `
                    <span class='expandable-image-wrapper'>
                        <img src='${imageData}' style='max-width:200px;max-height:200px;cursor:pointer;' class='expandable-image' />
                        <a href='${imageData}' download='image_${Date.now()}.png' class='btn btn-sm btn-link' title='Download'><i class='fa fa-download'></i></a>
                    </span>
                `;
                let data = {
                        'message': messageHtml,
                        'sent_by': USER_ID,
                        'send_to': send_to,
                        'thread_id': thread_id
                };
                socket.send(JSON.stringify(data));
        };
        reader.readAsDataURL(file);
}

// Modal for expanded image
$(document).on('click', '.expandable-image', function() {
        let src = $(this).attr('src');
        let modalHtml = `
            <div id='image-modal-overlay' style='position:fixed;top:0;left:0;width:100vw;height:100vh;background:rgba(0,0,0,0.8);z-index:9999;display:flex;align-items:center;justify-content:center;'>
                <img src='${src}' style='max-width:90vw;max-height:90vh;border:4px solid #fff;border-radius:8px;box-shadow:0 0 20px #000;' />
                <a href='${src}' download='image_${Date.now()}.png' class='btn btn-light' style='position:absolute;top:20px;right:80px;z-index:10000;'><i class='fa fa-download'></i> Download</a>
                <span id='close-image-modal' style='position:absolute;top:20px;right:20px;font-size:2.5rem;color:#fff;cursor:pointer;z-index:10000;'>&times;</span>
            </div>
        `;
        $('body').append(modalHtml);
});

$(document).on('click', '#close-image-modal', function() {
        $('#image-modal-overlay').remove();
});

function handleFileUpload(file) {
    if (!file) return;
    let reader = new FileReader();
    reader.onload = function(e) {
        let fileData = e.target.result;
        let send_to = get_active_other_user_id();
        let thread_id = get_active_thread_id();
        let fileName = file.name;
        let fileType = file.type;
        let icon = '<i class="fa fa-paperclip"></i>';
        let downloadLink = `<a href='${fileData}' download='${fileName}' target='_blank'>${icon} ${fileName}</a>`;
        let data = {
            'message': downloadLink,
            'sent_by': USER_ID,
            'send_to': send_to,
            'thread_id': thread_id
        };
        socket.send(JSON.stringify(data));
    };
    reader.readAsDataURL(file);
}

function get_active_other_user_id() {
    let other_user_id = $('.messages-wrapper.is_active').attr('other-user-id')
    other_user_id = $.trim(other_user_id)
    return other_user_id
}

function get_active_thread_id() {
    let chat_id = $('.messages-wrapper.is_active').attr('chat-id')
    let thread_id = chat_id.replace('chat_', '')
    return thread_id
}

// when load
scrollToBottom($('.messages-wrapper.is_active .chat-history'));  // chat-history inside the active chat
function scrollToBottom(element) {
    element.scrollTop(element[0].scrollHeight); // first DOM element
}