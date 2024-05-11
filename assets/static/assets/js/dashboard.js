$(function() {
    /////////////////////////////////////////////////////////////
    //
    /////////////////////////////////////////////////////////////
    const modal_ticker = new bootstrap.Modal(document.getElementById("modal-ticker"))

    htmx.on("htmx:afterSwap", (e) => {
        // Response targeting #dialog => show the modal
        if (e.detail.target.id == "ticker-form-dialog") {
            modal_ticker.show()
        };
    });

    htmx.on("htmx:beforeSwap", (e) => {
        // Empty response targeting #dialog => hide the modal
        if (e.detail.target.id == "ticker-form-dialog" && !e.detail.xhr.response) {
            modal_ticker.hide()
            e.detail.shouldSwap = false
        }
    })

});
