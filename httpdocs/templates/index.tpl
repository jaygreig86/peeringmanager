{include file="header.tpl"}
<script type="text/javascript">
    function load_content(div) {
        switch(div){
            case '#v-pills-routers':
                $(div).load('/content.php?function=viewrouters');
                break;
            case '#v-pills-bgppeers':
                $(div).load('/content.php?function=viewbgppeers');
                break;                
            case '#v-pills-bgpsessions':
                $(div).load('/content.php?function=viewbgpsessions');
                break;   
            case '#v-pills-logs':
                $(div).load('/content.php?function=viewlogs');
                break;           
            case '#v-pills-settings':
                $(div).load('/content.php?function=viewsettings');
                break;               
        }      
   }
    window.addEventListener('load', () => {
        $("button[id^=v-pills-]").click(function () {
            load_content($(this).data('bs-target'));
        });
    });    
</script>

<div class="container-fluid">
    <div class="row">
    <div class="col">
      &nbsp;
    </div>
    </div>
  <div class="row">
    <div class="col-md-2">
       {include file="menu-left.tpl"}
     
    </div>
    <div class="col-md-8">
          <div class="tab-content" id="v-pills-tabContent">
            <div class="tab-pane fade show active" id="v-pills-home" role="tabpanel" aria-labelledby="v-pills-home-tab" tabindex="0">Home</div>
            <div class="tab-pane fade" id="v-pills-routers" role="tabpanel" aria-labelledby="v-pills-routers-tab" tabindex="0">Routers</div>
            <div class="tab-pane fade" id="v-pills-bgppeers" role="tabpanel" aria-labelledby="v-pills-bgppeers-tab" tabindex="0">BGP Peers</div>
            <div class="tab-pane fade" id="v-pills-bgpsessions" role="tabpanel" aria-labelledby="v-pills-bgpsessions-tab" tabindex="0">BGP Sessions</div>            
            <div class="tab-pane fade" id="v-pills-settings" role="tabpanel" aria-labelledby="v-pills-settings-tab" tabindex="0">Settings</div>
            <div class="tab-pane fade" id="v-pills-logs" role="tabpanel" aria-labelledby="v-pills-logs-tab" tabindex="0">Logs</div>
          </div>    
    </div>
    <div class="col">
      &nbsp;
    </div>
  </div>
</div>


{include file="footer.tpl"}
