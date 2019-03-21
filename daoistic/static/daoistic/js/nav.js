function navigate(direction) {
    curr = window.location.pathname.split("/")
    if (curr[2] === undefined) {
        if (curr[1]) {
            curr = ["", curr[1], "page", "1"];
        } else {
            curr = ["", "poems", "page", "1"];
        }
    }
    if (curr[2] == "page") {
        if (direction == "previous") {
            curr[3] = ((parseInt(curr[3]) - 1) + 9 - 1) % 9 + 1;
            window.location.href = curr.join("/");
        }
        if (direction == "next") {
            curr[3] = ((parseInt(curr[3]) - 1) + 1) % 9 + 1;
            window.location.href = curr.join("/");
        }
    } else if (curr[2] == "chapter") {
        fetch(
            ["", "nav", curr[3], direction].join("/")
        ).then(function(response) {
            return response.json();
        }).then(function(navData) {
            curr[3] = navData.navTo;
            window.location.href = curr.join("/");
        }).catch(function(err) {
            console.log(err);
        });
    }
}
/* Keyboard navigation. */
$(window).on('keydown', function(ev) {
    if (ev.keyCode == 39) {
        navigate("next");
    } else if (ev.keyCode == 37) {
        navigate("previous");
    }
});
/* Swipe navigation. */
$(window).on('touchstart', function(ev) {
    window.startX = ev.originalEvent.changedTouches[0].pageX;
    window.startY = ev.originalEvent.changedTouches[0].pageY;
}).on('touchend', function(ev) {
    var diffY = startY - ev.originalEvent.changedTouches[0].pageY;
    if (Math.abs(diffY) > 25) { return true; }
    var diffX = startX - ev.originalEvent.changedTouches[0].pageX;
    if (diffX > 100) {
        navigate("next");
    } else if (diffX < -100) {
        navigate("previous");
    }
});
