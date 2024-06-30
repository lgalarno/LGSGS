htmx.onLoad(function() {
    /////////////////////////////////////////////////////////////
    // DataTable
    /////////////////////////////////////////////////////////////
    $('#table_assets').DataTable({
        columnDefs: [
            { orderable: false,
                targets: -1 }
            ],
        searching: false,
        bPaginate: false,
        info: false,
        order: [],
        processing: true,
        deferRender: true,
        bDestroy: true
    });

    $('#table_profits').DataTable({
        columnDefs: [
            { orderable: false,
                targets: -1 }
            ],
        searching: false,
        bPaginate: true,
        info: false,
        order: [],
        processing: true,
        deferRender: true,
        bDestroy: true
    });
    document.body.addEventListener('htmx:afterRequest', function(evt) {
        table_assetsDataTable.ajax.reload(function() {
            htmx.process('#table_assets');
        }, false)
        table_profitsDataTable.ajax.reload(function() {
            htmx.process('#table_profits');
        }, false)
});


 })
