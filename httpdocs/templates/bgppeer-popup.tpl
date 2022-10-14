<div id="infopopup" class="modal fade" role="dialog" tabindex="-1">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h4 class="modal-title"><span class="title"></span></h4>
                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body">
                <div class="container-fluid">
                    <div class="row">
                        <div class="col text-center">
                            <strong>Altering <span class="asn"></span></strong>
                        </div>
                    </div>
                    <form id="update_peer" class="row g-3" method="POST" action="_self">
                        <input type="hidden" class="peerid" name="peerid" id="peerid" value=""/>
                        <div class="col-md-6">
                          <label for="description" class="form-label">Description</label>
                          <input type="text" class="form-control description" id="description" name="description" maxlength="128" minlength="1" required>
                        </div>
                        <div class="col-md-6">
                          <label for="import" class="form-label">Import</label>
                          <input type="text" class="form-control import" id="import" name="import" placeholder="" maxlength="32" minlength="1" required>
                          <span class="suggest_import" id="suggest_import"></span>
                        </div>
                        <div class="col-md-6">
                          <label for="export" class="form-label">Export</label>
                          <input type="text" class="form-control export" id="export" name="export" placeholder="" maxlength="32" minlength="1" required value="{$settings.default_export}">
                        </div>
                        <div class="col-md-6">
                          <label for="ipv4limit" class="form-label">IPv4 Limit</label>
                          <input type="text" class="form-control ipv4_limit" id="ipv4_limit" name="ipv4_limit" max="4294967295" min="1" required>
                          <span class="suggest_ipv4_limit" id="suggest_ipv4_limit"></span>
                        </div>
                        <div class="col-md-6">
                          <label for="ipv6limit" class="form-label">IPv6 Limit</label>
                          <input type="text" class="form-control ipv6_limit" id="ipv6_limit" name="ipv6_limit" max="4294967295" min="1" required>
                          <span class="suggest_ipv6_limit" id="suggest_ipv6_limit"></span>                          
                        </div>
                        <div class="col-md-12">
                        <center>
                          <button type="submit" class="btn btn-success">Update Peer</button>
                        </center>
                        </div>            
                    </form>
                </div>
            </div>
        </div>
    </div>
</div>
<script>

    const handleInfoPopup = (event) => {
        let data = event.relatedTarget.dataset
        let modal = document.getElementById('infopopup')
        modal.getElementsByClassName('asn')[0].innerText = data.asn
        modal.getElementsByClassName('peerid')[0].value = data.peerid        
        modal.getElementsByClassName('description')[0].value = data.description
        modal.getElementsByClassName('import')[0].value = data.import
        modal.getElementsByClassName('export')[0].value = data.export
        modal.getElementsByClassName('ipv4_limit')[0].value = data.ipv4_limit
        modal.getElementsByClassName('ipv6_limit')[0].value = data.ipv6_limit
        modal.getElementsByClassName('suggest_import')[0].innerText = ""
        modal.getElementsByClassName('suggest_ipv4_limit')[0].innerText = ""
        modal.getElementsByClassName('suggest_ipv6_limit')[0].innerText = ""
        if (data.hasOwnProperty("notes")) {
            modal.getElementsByClassName('notes')[0].innerText = data.notes
        }
        
        edit_suggestions(data.asn,modal)
    }
    
        /* Lets retrieve all the information that we can from peeringdb */
    function edit_suggestions(asn,modal)
    {
       $.ajax({
            type: "GET",          
            url: "https://www.peeringdb.com/api/net?asn__in="+asn,
            headers: {
                "Authorization" : "Api-Key {$settings.peeringdb_api_key}"
            },
            success: function(msg) {
                console.log('working: '+JSON.stringify(msg));
                if (msg['data'].length){
                    modal.getElementsByClassName('suggest_import')[0].innerText = "Suggested: " + msg['data'][0]['irr_as_set'];
                    modal.getElementsByClassName('suggest_ipv4_limit')[0].innerText = "Suggested: " + Math.ceil(msg['data'][0]['info_prefixes4']*1.1);
                    modal.getElementsByClassName('suggest_ipv6_limit')[0].innerText = "Suggested: " + Math.ceil(msg['data'][0]['info_prefixes6']*1.1);
                }
                            },
            error: function(msg) {
                console.log('not working '+msg);

            }
        });                  
   }  

</script>
