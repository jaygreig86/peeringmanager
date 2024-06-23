<script type="text/javascript">
$(document).ready(function() {
    // The page we're working on
    var div = '#v-pills-bgpsessions';
    
   // When the document loads, fadeout any alerts within 8 seconds
    //$(".alert").fadeOut(8000);    
   $("#type").change(function(){
       if ($("#type").val() === 'customer'){
           $("#send").prop('disabled', false);
       } else $("#send").prop('disabled', 'disabled');
   });
   $('#show_add_session').click(function() {
       $('#sessions_add').slideDown("slow");
   });

   $("#add_session").submit(function(e) {
        e.preventDefault();
        var dataString = $(this).serialize();
        $.ajax({
            type: "POST",
            url: "content.php?function=addbgpsession",
            data: dataString,
            success: function(msg) {
                console.log('working: '+msg);
                load_content(div);
            },
            error: function(msg) {
                console.log('not working '+msg);
                load_content(div);
            }
        });        
   });
    $("a[id^=reset]").click(function(e){
        e.preventDefault();
        var dataString = $(this).data("sessionid");
        $.ajax({
            type: "GET",
            url: "content.php?function=resetbgpsession&sessionid=" + dataString,
            success: function(msg) {
                //$("#ratesucess").html("working");  
                console.log('working: '+msg);
                load_content(div);
            },
            error: function(msg) {
                //$("#ratesucess").html("not working ");  
                console.log('not working '+msg);
                load_content(div);
            }
        });        
   });      
    $("a[id^=delete]").click(function(e){
        e.preventDefault();
        var dataString = $(this).data("sessionid");
        $.ajax({
            type: "GET",
            url: "content.php?function=deletebgpsession&sessionid=" + dataString,
            success: function(msg) {
                //$("#ratesucess").html("working");  
                console.log('working: '+msg);
                load_content(div);
            },
            error: function(msg) {
                //$("#ratesucess").html("not working ");  
                console.log('not working '+msg);
                load_content(div);
            }
        });        
   });   
});
</script>
<script type="text/javascript">
    $(document).ready(function () {
        let table = $('#bgpsessionslist').DataTable({
            "dom": '<"row"<"col ms-auto"p><"col"f><"col align-middle"l>><"row"i>t<"row"<"col"p>>',
            "iDisplayLength": 100,
            "lengthMenu": [[15, 25, 50, -1], [15, 25, 50, "All"]],
            "pageLength": 100,
            "order": [[0, "asc"], [3, "asc"], [2, "asc"]],
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
    
<!-- Begin main content -->

<div class="row"><center><button id="show_add_session" type="button" title="Add New" class="btn btn-primary">Add BGP Session <i class="fa-solid fa-caret-down"></i></button></center></div>
    <div class="row" id="sessions_add" style="display: none">
        <form id="add_session" class="row g-3" method="POST" action="_self">
            <div class="col-md-6">
              <label for="peerid" class="form-label">ASN</label>
                <select class="form-control" name="peerid" id="peerid" required>
                    <option disabled selected value>Select an ASN</option>
                    {foreach from=$bgppeers key=k item=peer}
                    <option value="{$peer.peerid}">{$peer.asn} - {$peer.description|truncate:30}</option>
                    {/foreach}
                </select>
            </div>
            <div class="col-md-6">
              <label for="routerid" class="form-label">Router</label>
                <select class="form-control" name="routerid" id="routerid" required>
                    <option disabled selected value>Select a Router</option>
                    {foreach from=$routers key=k item=router}
                    <option value="{$router.routerid}">{$router.hostname}</option>
                    {/foreach}
                </select>
            </div>                
            <div class="col-md-6">
              <label for="address" class="form-label">Address</label>
              <input type="text" class="form-control" id="address" name="address" minlength="7" maxlength="64" required>
            </div>
            <div class="col-md-6">
              <label for="password" class="form-label">Password</label>
              <input type="text" class="form-control" id="password" name="password" minlength="1" maxlength="80" >
            </div>                
            <div class="col-md-6">
              <label for="type" class="form-label">Session Type</label>                
                <select class="form-control" name="type" id="type" required>
                    <option disabled selected value></option>
                    <option value="peer">Peer</option>
                    <option value="customer">Customer</option>
                </select>
            </div>
            <div class="col-md-6">
              <label for="send" class="form-label">Announcement Setting</label>                
                <select class="form-control" name="send" id="send" required disabled>
                    <option disabled selected value></option>
                    <option value="default_only">Default Only</option>
                    <option value="customers_only">Customers Only</option>
                    <option value="customers_default">Customers + Default</option>
                    <option value="customers_peers_default">Customers + Peers + Default</option> 
                    <option value="customers_peers">Customers + Peers</option>                    
                    <option value="full">Full Table</option>                    
                </select>
            </div>                
            <div class="col-md-12">
            <center>
              <button type="submit" class="btn btn-success">Add Session</button>
            </center>
            </div>            
        </form>
    </div>
<!-- begin list -->
<row class="mb-3">&nbsp;</row>
<table class="table table-striped table-framed order-column" id="bgpsessionslist">
    <thead>
        <tr>
            <th class="textcenter">ASN</th>
            <th class="textcenter">Description</th>
            <th class="textcenter">Type</th>
            <th class="textcenter">Address</th>
            <th class="textcenter">Password</th>
            <th class="textcenter">Router</th>
            <th class="textcenter">Send</th>
            <th class="textcenter"></th>
        </tr>
    </thead>
    <tbody>
        {foreach from=$bgpsessions key=k item=session}
            <tr>
                <td style="padding: 2px">{$session.asn}</td>  
                <td style="padding: 2px">{$session.description}</td>  
                <td style="padding: 2px">{$session.type}</td>  
                <td style="padding: 2px">{$session.address}</td>  
                <td style="padding: 2px">{$session.password}</td>  
                <td style="padding: 2px">{$session.hostname}</td>
                <td style="padding: 2px">{$session.send}</td>
                <td style="padding: 2px" align="right">
                    <!-- Example single danger button -->
                    <div class="btn-group">
                      <button type="button" class="btn btn-primary dropdown-toggle" data-bs-toggle="dropdown" aria-expanded="false">
                        Action
                      </button>
                      <ul class="dropdown-menu">
                        <li><a class="dropdown-item" id="reset{$session.sessionid}" data-sessionid="{$session.sessionid}" href="#">Reset Session</a></li>
                        <li><a class="dropdown-item" id="delete{$session.sessionid}" data-sessionid="{$session.sessionid}" href="#">Delete Session</a></li>
                      </ul>
                    </div>     
                </td> 
            </tr>
        {/foreach}
    </tbody>
</table>

