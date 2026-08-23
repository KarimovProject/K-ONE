import os
import re

filepath = 'C:/IEMS/templates/base.html'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

js_snippet = """
<script>
document.addEventListener('DOMContentLoaded', function() {
  document.body.addEventListener('click', function(e) {
    // Close all dropdowns
    var allDropdowns = document.querySelectorAll('.premium-dropdown-menu');
    
    // Find closest toggle
    var toggle = e.target.closest('.dropdown-toggle');
    
    if (toggle) {
      e.preventDefault();
      e.stopPropagation();
      var wrapper = toggle.closest('.dropdown-wrapper');
      var menu = wrapper.querySelector('.premium-dropdown-menu');
      var isHidden = menu.hasAttribute('hidden');
      
      allDropdowns.forEach(d => d.setAttribute('hidden', 'hidden'));
      
      if (isHidden) {
        menu.removeAttribute('hidden');
      }
    } else {
      allDropdowns.forEach(d => d.setAttribute('hidden', 'hidden'));
    }
  });
});
</script>
</body>
"""

content = content.replace('</body>', js_snippet)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print("Added JS to base.html")
