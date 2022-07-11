<script type="text/javascript">
$(document).ready(function() {
    // The page we're working on
    var div = '#v-pills-settings';

   $("#add_peer").submit(function(e) {
        e.preventDefault();
        var dataString = $(this).serialize();
        $.ajax({
            type: "POST",
            url: "content.php?function=updatesettings",
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



    
<div class="row">
<form id="add_peer" class="row g-3" method="POST" action="_self">
    {foreach from=$settings key=k item=setting}
        <div class="col-md-6">
          <label for="{$k}" class="form-label">{$k}</label>
          <input type="text" class="form-control" id="{$k}" name="{$k}" value="{$setting}" required>
        </div>
    {/foreach}
   
    <div class="col-md-12">
    <center>
      <button type="submit" id="savesettings" name="savesettings" class="btn btn-success">Save</button>
    </center>
    </div>            
</form>
</div>