
// 🔒 ShadowWall Injecter - Password Blocker
window.onload = function() {
  document.querySelectorAll("input[type='password']").forEach(el => el.disabled = true);
  document.querySelectorAll("form").forEach(form => {
    form.addEventListener("submit", function(e) {
      e.preventDefault();
      alert("🛘 ShadowWall blocked password submission on this fake site!");
    });
  });
  window.scrollTo(0, document.body.scrollHeight);
};

