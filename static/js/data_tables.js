htmx.onLoad(function() {
    /////////////////////////////////////////////////////////////
    // DataTable
    /////////////////////////////////////////////////////////////
    $('#table_list').DataTable({
        columnDefs: [
            { orderable: false,
                targets: -1 }
            ],
        searching: true,
        bPaginate: true,
        pageLength: 25,
        info: false,
        order: [],
        processing: true,
        deferRender: true,
        bDestroy: true,
        language: {"search": "Filter:"}
    });

    $('#table_pages').DataTable({
        columnDefs: [
            { orderable: false,
                targets: -1 }
            ],
        searching: true,
        bPaginate: true,
        pageLength: 25,
        info: false,
        order: [],
        processing: true,
        deferRender: true,
        bDestroy: true,
        language: {"search": "Filter:"}
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
