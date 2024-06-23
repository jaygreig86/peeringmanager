<script type="text/javascript">
$(document).ready(function() {
    // The page we're working on
    var div = '#v-pills-bgppeers';
    
    // Handle the Edit popup
    document.getElementById("infopopup").addEventListener('show.bs.modal', handleInfoPopup)

   // When the document loads, fadeout any alerts within 8 seconds
    $(".alert").fadeOut(8000);    
    
   $('#show_add_peers').click(function() {
       $('#peers_add').slideDown("slow");
   });

   $("#add_peer").submit(function(e) {
        e.preventDefault();
        var dataString = $(this).serialize();
        $.ajax({
            type: "POST",
            url: "content.php?function=addbgppeer",
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
   
   /* Update a BGP Peer in the background */
   $("#update_peer").submit(function(e) {
        e.preventDefault();
        var dataString = $(this).serialize();
        $('.modal').modal('hide');
        $.ajax({
            type: "POST",
            url: "content.php?function=updatebgppeer",
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
   
   /* Lets retrieve all the information that we can from peeringdb */
   $("#asn").change(function(){
       var asn = $('#asn').val();
       $.ajax({
            type: "GET",          
            url: "https://www.peeringdb.com/api/net?asn__in="+asn,
            headers: {
                "Authorization" : "Api-Key {$settings.peeringdb_api_key}"
            },
            success: function(msg) {
                console.log('working: '+JSON.stringify(msg));
                if (msg['data'].length){
                    $('#import').val(msg['data'][0]['irr_as_set']);
                    $('#description').val(msg['data'][0]['name']);
                    $('#ipv4_limit').val(Math.ceil(msg['data'][0]['info_prefixes4']*1.1));
                    $('#ipv6_limit').val(Math.ceil(msg['data'][0]['info_prefixes6']*1.1));
                }   
                unlock_fields();
            },
            error: function(msg) {
                console.log('not working '+msg);
                unlock_fields();

            }
        });                  
   });   
   
    $("a[id^=delete]").click(function(e){
        e.preventDefault();
        var dataString = $(this).data("peerid");
        $.ajax({
            type: "GET",
            url: "content.php?function=deletebgppeer&peerid=" + dataString,
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
   
   // When a new peer has been added we can build the configuration after
   // adding sessions
   
    $("a[id^=configure]").click(function(e){
        e.preventDefault();
        var dataString = $(this).data("peerid");
        $.ajax({
            type: "GET",
            url: "content.php?function=configurebgppeer&peerid=" + dataString,
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
   
    $("a[id^=build]").click(function(e){
        e.preventDefault();
        var dataString = $(this).data("peerid");
        $.ajax({
            type: "GET",
            url: "content.php?function=buildfilters&peerid=" + dataString,
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
   function unlock_fields()
   {
       $('#import').prop('disabled', false);
       $('#description').prop('disabled', false);
       $('#ipv4_limit').prop('disabled', false);
       $('#ipv6_limit').prop('disabled', false);
   }
   function lock_fields()
   {
       $('#import').prop('disabled', true);
       $('#description').prop('disabled', true);
       $('#ipv4_limit').prop('disabled', true);
       $('#ipv6_limit').prop('disabled', true);       
   }
   lock_fields();
});
</script>
<script type="text/javascript">
    $(document).ready(function () {
        let table = $('#bgppeerslist').DataTable({
            "dom": '<"row"<"col ms-auto"p><"col"f><"col align-middle"l>><"row"i>t<"row"<"col"p>>',
            "iDisplayLength": 100,
            "lengthMenu": [[15, 25, 50, -1], [15, 25, 50, "All"]],
            "pageLength": 100,
            "order": [[1, "asc"], [3, "asc"], [2, "asc"]],
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


<div class="row"><center><button id="show_add_peers" type="button" title="Add New" class="btn btn-primary">Add BGP Peer <i class="fa-solid fa-caret-down"></i></button></center></div>
    <div class="row" id="peers_add" style="display: none">
        <form id="add_peer" class="row g-3" method="POST" action="_self">
            <div class="col-md-6">
              <label for="asn" class="form-label">ASN</label>
                <div class="input-group mb-4">
                  <input type="number" class="form-control" id="asn" name="asn" max="4294967295" min="1" placeholder="Enter an ASN number to start" required aria-describedby="fetchbutton">
                    <button class="btn btn-success" type="button" id="fetchbutton">Fetch</button>
                </div>              
            </div>

            <div class="col-md-6">
              <label for="description" class="form-label">Description</label>
              <input type="text" class="form-control" id="description" name="description" maxlength="128" minlength="1" required>
            </div>
            <div class="col-md-6">
              <label for="import" class="form-label">Import</label>
              <input type="text" class="form-control" id="import" name="import" placeholder="" maxlength="32" minlength="1" required>
            </div>
            <div class="col-md-6">
              <label for="export" class="form-label">Export</label>
              <input type="text" class="form-control" id="export" name="export" placeholder="" maxlength="32" minlength="1" required value="{$settings.default_export}">
            </div>
            <div class="col-md-6">
              <label for="ipv4limit" class="form-label">IPv4 Limit</label>
              <input type="text" class="form-control" id="ipv4_limit" name="ipv4_limit" max="4294967295" min="1" required>
            </div>
            <div class="col-md-6">
              <label for="ipv6limit" class="form-label">IPv6 Limit</label>
              <input type="text" class="form-control" id="ipv6_limit" name="ipv6_limit" max="4294967295" min="1" required>
            </div>
            <div class="col-md-12">
            <center>
              <button type="submit" class="btn btn-success">Add Peer</button>
            </center>
            </div>            
        </form>
    </div>
<!-- begin list -->
<row class="mb-3">&nbsp;</row>
<table class="table table-striped table-framed order-column" id="bgppeerslist">
    <thead>
        <tr>
            <th class="textcenter">ASN</th>
            <th class="textcenter">Description</th>
            <th class="textcenter">Import</th>
            <th class="textcenter">Export</th>
            <th class="textcenter">IPv4 Limit</th>
            <th class="textcenter">IPv6 Limit</th>
            <th class="textcenter"></th>
        </tr>
    </thead>
    <tbody>
        {foreach from=$bgppeers key=k item=peer}
            <tr>
                <td style="padding: 2px">{$peer.asn}</td>  
                <td style="padding: 2px">{$peer.description}</td>  
                <td style="padding: 2px">{$peer.import}</td>  
                <td style="padding: 2px">{$peer.export}</td>  
                <td style="padding: 2px">{$peer.ipv4_limit}</td>  
                <td style="padding: 2px">{$peer.ipv6_limit}</td>  
                <td style="padding: 2px" align="right">
                    <!-- Example single danger button -->
                    <div class="btn-group">
                      <button type="button" class="btn btn-primary dropdown-toggle" data-bs-toggle="dropdown" aria-expanded="false">
                        Action
                      </button>
                      <ul class="dropdown-menu">
                          <li><a class="infopopup dropdown-item"
                             data-bs-toggle="modal"
                             data-bs-target="#infopopup"
                             data-peerid="{$peer.peerid}"
                             data-asn="{$peer.asn}" 
                             data-description="{$peer.description}"
                             data-import="{$peer.import}"
                             data-export="{$peer.export}"
                             data-ipv4_limit="{$peer.ipv4_limit}"
                             data-ipv6_limit="{$peer.ipv6_limit}"
                             id="edit{$peer.peerid}"
                             href="#">Edit Peer</a></li>
                             <li><a class="dropdown-item" id="configure{$peer.peerid}" data-peerid="{$peer.peerid}" href="#">Build Peer Config</a></li>
                             <li><a class="dropdown-item" id="build{$peer.peerid}" data-peerid="{$peer.peerid}" href="#">Build Filters</a></li>
                        <li><a class="dropdown-item" id="delete{$peer.peerid}" data-peerid="{$peer.peerid}" href="#">Delete Peer</a></li>
                      </ul>
                    </div>     
                </td> 
            </tr>
        {/foreach}
    </tbody>
</table>
{include file="bgppeer-edit-popup.tpl"}