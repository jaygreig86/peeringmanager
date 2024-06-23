<script type="text/javascript">
    $(document).ready(function () {
        let table = $('#logs').DataTable({
            "dom": '<"row"<"col ms-auto"p><"col"f><"col align-middle"l>><"row"i>t<"row"<"col"p>>',
            "iDisplayLength": 100,
            "lengthMenu": [[15, 25, 50, -1], [15, 25, 50, "All"]],
            "pageLength": 100,
            "order": [[0, "desc"], [3, "asc"], [2, "asc"]],
            "search": {
                "return": true,
                "search": "{$smarty.get.search}"
            },
        });
        table.on( 'search.dt', function () {
            let url = new URL(window.location);
            url.searchParams.set('search', table.search());
            window.history.pushState(null, '', url.toString());
        });
    });
</script>


<!-- lets display alerts at the top of the page -->

<div class="row">
    <center>
    <div class="col">
        {foreach from=$alerts key=k item=alert}
            <div id="alert{$k}" class="alert {$alert.type}" role="alert">
                {$alert.message}
            </div>
        {/foreach}
    </div>
    </center>
</div>

<!-- begin list -->
<row class="mb-3">&nbsp;</row>
<table class="table table-striped table-framed order-column" id="logs">
    <thead>
        <tr>
            <th class="textcenter">Log ID</th>
            <th class="textcenter">Date/Time</th>
            <th class="textcenter">User</th>
            <th class="textcenter">Type</th>
            <th class="textcenter">IP</th>
            <th class="textcenter">Log Entry</th>
        </tr>
    </thead>
    <tbody>
        {foreach from=$logs key=k item=log}
            <tr>
                <td style="padding: 2px">{$log.logid}</td>  
                <td style="padding: 2px">{$log.datetime}</td>  
                <td style="padding: 2px">{$log.username}</td>  
                <td style="padding: 2px">{$log.type}</td>  
                <td style="padding: 2px">{$log.userip}</td>  
                <td style="padding: 2px">{$log.logentry}</td>
            </tr>
        {/foreach}
    </tbody>
</table>

