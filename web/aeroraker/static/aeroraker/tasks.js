function get_tasks(task_url) {
    $.ajax({
    url: task_url,
    success: function(response_data) {
        var data = [];
        data.push(
            '<table>' +
            '<tr>' +
            '<th>id</th> <th>completed</th>' +
            '<th>origin</th> <th>destination</th>' +
            '<th>search_date_start</th> <th>search_date_end</th>' +
            '<th>ts</th>' +
            '</tr>'
        );
        $.each(response_data, function(i, o) {
            if (o["completed"] == "100%") {
                data.push("<tr>");
            } else {
                data.push('<tr class="is_not_done">');
            }
            data.push(
                "<td><a href=\"" + o["url"] + "\">" + o["id"] + "</td>" +
                "<td>" + o["completed"] + "</td>" +
                "<td>" + o["origin"] + "</td>" +
                "<td>" + o["destination"] + "</td>" +
                "<td>" + o["search_date_start"] + "</td>" +
                "<td>" + o["search_date_end"] + "</td>" +
                "<td nowrap>" + new Date(o["ts"]) + "</td>" +
                "</tr>"
            );
        });
        data.push('</table>');
        $("#tasks_table").html(data.join(""));
    },
    complete: function() {
        setTimeout(get_tasks, 1000, task_url);
    }
    });
}
