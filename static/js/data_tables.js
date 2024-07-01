htmx.onLoad(function() {
    /////////////////////////////////////////////////////////////
    // DataTable
    /////////////////////////////////////////////////////////////
    $('#table_list').DataTable({
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

    $('#table_pages').DataTable({
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
        table_listDataTable.ajax.reload(function() {
            htmx.process('#table_list');
            htmx.process('#table_pages');
        }, false)
        // table_pagesDataTable.ajax.reload(function() {
        //     htmx.process('#table_pages');
        // }, false)
});


 })
