const forms = document.querySelectorAll("form");
forms.forEach(form => {
  form.addEventListener("submit", function(e) {
    e.preventDefault();
    alert("🚨 ShadowWall blocked this suspicious login page!");
  });
});
