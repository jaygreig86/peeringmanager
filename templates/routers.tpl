<script type="text/javascript">
$(document).ready(function() {
    // The page we're working on
    var div = '#v-pills-routers';
   // When the document loads, fadeout any alerts within 8 seconds
    $(".alert").fadeOut(8000);    
    
   $('#show_add').click(function() {
       $('#routers_add').slideDown("slow");
   });

   $("#add_router").submit(function(e) {
        e.preventDefault();
        var dataString = $(this).serialize();
        $.ajax({
            type: "POST",
            url: "content.php?function=addrouter",
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
    $("a[id^=delete]").click(function(e){
        e.preventDefault();
        var dataString = $(this).data("routerid");
        $.ajax({
            type: "GET",
            url: "content.php?function=deleterouter&routerid=" + dataString,
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


<div class="row"><center><button id="show_add" type="button" title="Add New" class="btn btn-primary">Add New Router <i class="fa-solid fa-caret-down"></i></button></center></div>
         <div class="row" id="routers_add" style="display: none">
             <form id="add_router" class="form-horizontal" method="POST" action="_self">
             <table class="table table-striped table-framed" >
			<thead>
                            <tr>
                    <th class="textcenter">Router Hostname</th>
                    <th class="textcenter">Router Type</th>
                    <th class="textcenter">Action</th>
                            </tr>
			</thead>
			<tbody>
            
            	<tr>
                    <td>
    <div class="form-group mb-4">
      <input class="form-control" id="hostname" name="hostname" maxlength="255" minlength="4" type="text" value="" placeholder="router.host.tld" required/>
  </div>
</td>       
                        
                  
<td>
    <div class="form-group mb-4">
      <select class="form-control" name="routertypeid" id="routertypeid" required>
          <option disabled selected value></option>
          {foreach from=$routertypes key=k item=routertype}
          <option value="{$routertype.routertypeid}">{$routertype.vendor}</option>
          {/foreach}
      </select>
  </div>
</td>                   
                   <td><button type="submit" class="btn btn-success">Add</button></td>
               
                </tr>

            </tbody>
		</table>
             </form>
         </div>
<!-- being list -->
<table class="table table-striped table-framed order-column" id="primary-table-list">
    <thead>
        <tr>
            <th class="textcenter">Router ID</th>
            <th class="textcenter">Hostname</th>
            <th class="textcenter">Vendor</th>
            <th class="textcenter"></th>
        </tr>
    </thead>
    <tbody>
        {foreach from=$routers key=k item=router}
            <tr>
                <td style="padding: 2px">{$router.routerid}</td>  
                <td style="padding: 2px">{$router.hostname}</td>  
                <td style="padding: 2px">{$router.vendor}</td> 
                <td style="padding: 2px">
                    <!-- Example single danger button -->
                    <div class="btn-group">
                      <button type="button" class="btn btn-primary dropdown-toggle" data-bs-toggle="dropdown" aria-expanded="false">
                        Action
                      </button>
                      <ul class="dropdown-menu">
                        <li><a class="dropdown-item" id="delete{$router.routerid}" data-routerid="{$router.routerid}" href="#">Delete Router</a></li>
                      </ul>
                    </div>     
                </td> 
            </tr>
        {/foreach}
    </tbody>
</table>
