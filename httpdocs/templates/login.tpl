{assign var="loginpage" value="true"}
{include file="header.tpl"}
<div class="container-fluid">
    <div class="row">
    <div class="col">
      top
    </div>
    </div>
  <div class="row justify-content-center">
    <div class="col">
      left side
    </div>
    <div class="col-md-4">
        <form class="login-form-container" method="POST" action="index.php">
          <!-- Username input -->
            <label class="form-label" for="username">Username</label>              
            <div class="input-group mb-4">
              {if $settings.ldap_enabled}<span class="input-group-text" id="basic-addon3">{$settings.ldap_domain}</span><span class="input-group-text">\</span>{/if}
              <input type="text" id="username" name="username" class="form-control" aria-describedby="basic-addon3">
            </div>
          <!-- Password input -->
            <label class="form-label" for="password">Password</label>          
          <div class="form-group mb-4">
            <input type="password" id="password" name="password" class="form-control" />
          </div>
          <!-- Submit button -->
          <button type="submit" class="btn btn-primary btn-block mb-4">Sign in</button>
        </form>
    </div>
    <div class="col">
      right side
    </div>
  </div>
</div>


{include file="footer.tpl"}
