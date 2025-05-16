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
        language: {
            "info": "Affichage de _START_ à _END_ sur _TOTAL_ entrées",
            "infoEmpty": "Affichage de 0 à 0 sur 0 entrées",
            "infoFiltered": "(filtrées depuis un total de _MAX_ entrées)",
            "lengthMenu": "Afficher _MENU_ entrées",
            "paginate": {
                "first": "Première",
                "last": "Dernière",
                "next": "Suivante",
                "previous": "Précédente"
            },
            "zeroRecords": "Aucune entrée correspondante trouvée",
            "aria": {
                "sortAscending": " : activer pour trier la colonne par ordre croissant",
                "sortDescending": " : activer pour trier la colonne par ordre décroissant"
            },
            "infoThousands": " ",
            "search": "Rechercher :",
            "thousands": " "
        },
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
        language: {
            "info": "Affichage de _START_ à _END_ sur _TOTAL_ entrées",
            "infoEmpty": "Affichage de 0 à 0 sur 0 entrées",
            "infoFiltered": "(filtrées depuis un total de _MAX_ entrées)",
            "lengthMenu": "Afficher _MENU_ entrées",
            "paginate": {
                "first": "Première",
                "last": "Dernière",
                "next": "Suivante",
                "previous": "Précédente"
            },
            "zeroRecords": "Aucune entrée correspondante trouvée",
            "aria": {
                "sortAscending": " : activer pour trier la colonne par ordre croissant",
                "sortDescending": " : activer pour trier la colonne par ordre décroissant"
            },
            "infoThousands": " ",
            "search": "Rechercher :",
            "thousands": " "
        }
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
        language: {
            "info": "Affichage de _START_ à _END_ sur _TOTAL_ entrées",
            "infoEmpty": "Affichage de 0 à 0 sur 0 entrées",
            "infoFiltered": "(filtrées depuis un total de _MAX_ entrées)",
            "lengthMenu": "Afficher _MENU_ entrées",
            "paginate": {
                "first": "Première",
                "last": "Dernière",
                "next": "Suivante",
                "previous": "Précédente"
            },
            "zeroRecords": "Aucune entrée correspondante trouvée",
            "aria": {
                "sortAscending": " : activer pour trier la colonne par ordre croissant",
                "sortDescending": " : activer pour trier la colonne par ordre décroissant"
            },
            "infoThousands": " ",
            "search": "Rechercher :",
            "thousands": " "
        },
    select: true,
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
