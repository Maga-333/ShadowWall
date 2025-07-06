from selenium import webdriver

driver = webdriver.Chrome()
driver.get("http://fake-login-site.com")

# Inject blocking JS
driver.execute_script("""
  document.querySelectorAll('input[type="password"]').forEach(el => el.disabled = true);
  alert("🚨 Blocked: Fake Login Page Detected!");
""")
