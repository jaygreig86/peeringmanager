<script type="text/javascript">
$(document).ready(function() {
    // The page we're working on
    var div = '#v-pills-bgppeers';
    
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
   /* Lets retrieve all the information that we can from peeringdb */
   $("#asn").change(function(){
       var asn = $('#asn').val();
       $.ajax({
            type: "GET",
//https://www.peeringdb.com/api/as_set/            
            url: "https://www.peeringdb.com/api/net?asn__in="+asn,
            headers: {
                "Authorization" : "Api-Key {$settings.peeringdb_api_key}"
            },
            success: function(msg) {
                console.log('working: '+JSON.stringify(msg));
//                alert(JSON.stringify(msg['data']));
                $('#import').val(msg['data'][0]['irr_as_set']);
                $('#description').val(msg['data'][0]['name']);
                $('#ipv4_limit').val(msg['data'][0]['info_prefixes4']);
                $('#ipv6_limit').val(msg['data'][0]['info_prefixes6']);
            },
            error: function(msg) {
                console.log('not working '+msg);

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
              <input type="number" class="form-control" id="asn" name="asn" max="4294967295" min="1" required>
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
<!-- being list -->
<table class="table table-striped table-framed order-column" id="primary-table-list">
    <thead>
        <tr>
            <th class="textcenter">ASN</th>
            <th class="textcenter">Description</th>
            <th class="textcenter"></th>
        </tr>
    </thead>
    <tbody>
        {foreach from=$bgppeers key=k item=peer}
            <tr>
                <td style="padding: 2px">{$peer.asn}</td>  
                <td style="padding: 2px">{$peer.description}</td>  
                <td style="padding: 2px" align="right">
                    <!-- Example single danger button -->
                    <div class="btn-group">
                      <button type="button" class="btn btn-primary dropdown-toggle" data-bs-toggle="dropdown" aria-expanded="false">
                        Action
                      </button>
                      <ul class="dropdown-menu">
                        <li><a class="dropdown-item" id="delete{$peer.peerid}" data-peerid="{$peer.peerid}" href="#">Delete Peer</a></li>
                      </ul>
                    </div>     
                </td> 
            </tr>
        {/foreach}
    </tbody>
</table>
