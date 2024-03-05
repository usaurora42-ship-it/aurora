$(function () {
    $(document).scroll(function (e) {
        var $nav = $(".navbar");
        $nav.toggleClass('scrolled', $(this).scrollTop() > $nav.height() * 0.1);
        var $nav = $(".inline-media");
        $nav.toggleClass('scrolled', $(this).scrollTop() > $nav.height() * 1);
        e.preventDefault();
    });

    if (!getCookie('acept_cookies_elasbank')) {
        $('#disclaimer_modal').modal('show')
    }

    $('button[id="btn_accept_cookies"]').on('click', function (e) {
        $('#disclaimer_modal').modal('hide')
        e.preventDefault();
        setCookie('acept_cookies_elasbank', true, 365)
    });

    $('button[id="close"]').on('click', function (e) {
        $('#modal_success').modal('hide')
        e.preventDefault();
    });

    $('input[type="tel"]').mask('(00) 00000-0000')
});