// From http://www.bootply.com/92189#
$(function() {
    var active = 0;
    var activeTitles = {};

    $('.btn-toggle').click(function() {
        var btn = $(this).find('.btn');
        btn.toggleClass('active');

        if ($(this).find('.btn-primary').size()>0) {
            btn.toggleClass('btn-primary');
        }
        if ($(this).find('.btn-danger').size()>0) {
            btn.toggleClass('btn-danger');
        }
        if ($(this).find('.btn-success').size()>0) {
            btn.toggleClass('btn-success');
        }
        if ($(this).find('.btn-info').size()>0) {
            btn.toggleClass('btn-info');
        }

        btn.toggleClass('btn-default');

        if (btn.hasClass('active')) {
            active++;
            activeTitles[$(this).siblings()[0].textContent.trim()] = true;
        } else {
            active--;
            delete activeTitles[$(this).siblings()[0].textContent.trim()];
        }
        if (active >= 2) {
            $('#merge-btn').removeClass('hidden')
        } else {
            $('#merge-btn').addClass('hidden')
        }
    });

    $('#merge-btn').click(function() {
        var params = {};
        var i = 1;
        for (var title in activeTitles) {
            params['c' + i] = title;
            i++;
        }
        var newURL = encodeURI('/merge?' + jQuery.param(params));
        window.location = newURL;
        console.log(newURL);
        return false;
    });
});
