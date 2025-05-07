htmx.onLoad(function() {
    /////////////////////////////////////////////////////////////
    // DataTable
    /////////////////////////////////////////////////////////////
    $('#table_book').DataTable({
        // columnDefs: [
        //     { orderable: false,
        //         targets: -1 }
        //     ],
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

    $('#table_list').DataTable({
        columnDefs: [
            { orderable: false,
                targets: -1 }
            ],
        searching: true,
        // bPaginate: true,
        // pageLength: 25,
        info: false,
        order: [],
        processing: true,
        deferRender: true,
        bDestroy: true,
        language: {"search": "Filter:"}
    });

    $('#table_pages').DataTable({
        // columnDefs: [
        //     { orderable: false,
        //         targets: -1 }
        //     ],
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
        DataTable.ajax.reload(function() {
            htmx.process('#table_list');
            htmx.process('#table_pages');
        }, false)
        // table_pagesDataTable.ajax.reload(function() {
        //     htmx.process('#table_pages');
        // }, false)
    });
 })
