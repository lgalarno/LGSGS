htmx.onLoad(function() {
     $('#table_book').DataTable({
        // columnDefs: [
        //     { orderable: false,
        //         targets: -1 }
        //     ],
        responsive: true,
        searching: true,
        bPaginate: true,
        pageLength: 25,
        info: false,
        order: [],
        processing: true,
        deferRender: true,
        bDestroy: true,

     layout: {
        topStart: {
            buttons: [
                {
                    extend: 'csvHtml5',
                    text: 'sauver en csv',
                    charset: 'utf-8',
                }
                ]
        }
    },
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

    /////////////////////////////////////////////////////////////
    // DataTable
    /////////////////////////////////////////////////////////////
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

 })
DataTable.Buttons.defaults.dom.button.className = 'btn btn-sm btn-primary';
