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
          <!-- Email input -->
          <div class="form-group mb-4">
            <input type="email" id="username" name="username" class="form-control" />
            <label class="form-label" for="username">Email address</label>
          </div>

          <!-- Password input -->
          <div class="form-group mb-4">
            <input type="password" id="password" name="password" class="form-control" />
            <label class="form-label" for="password">Password</label>
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
