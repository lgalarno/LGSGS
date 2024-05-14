$(function() {
    /////////////////////////////////////////////////////////////
    // DataTable
    /////////////////////////////////////////////////////////////
    $('#data_table').DataTable({
        searching: false,
        bPaginate: false,
        order: [],
        processing: true,
        deferRender: true,
        initComplete: function () {
                this.api()
                    .columns('.head')
                    .every(function () {
                        let column = this;
                        let select = $('<select><option value=""></option></select>')
                            .appendTo($("#data_table thead tr:eq(1) th").eq(column.index()).empty())
                            .on('change', function () {
                                var val = $.fn.dataTable.util.escapeRegex($(this).val());
                                column.search(val ? '^' + val + '$' : '', true, false).draw();
                            });
                        column
                            .data()
                            .unique()
                            .sort()
                            .each(function (d, j) {
                                select.append('<option value="' + d + '">' + d + '</option>');
                            });
                    });
            }
    });
 })
