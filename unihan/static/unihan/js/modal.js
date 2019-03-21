function unihanModal(event) {
    var character = $(event.target).attr("data-char");
    var modalId = $(event.target).attr("data-target");
    $(".modal-title").text("Unihan " + character);
    fetch(
        ["", "unihan", "info", character].join("/"),
    ).then(function(response) {
        return response.text();
    }).then(function(charInfo) {
        $(".modal-body").html(charInfo);
    }).catch(function(err) {
        console.log(err);
        $(".modal-body").text("Error loading character data.");
    });
    $(modalId).modal();
}
