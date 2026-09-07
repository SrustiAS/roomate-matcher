// Animate compatibility rings from their data-p attribute.
document.querySelectorAll('.ring').forEach(function(r){
  r.style.setProperty('--p', r.dataset.p || 0);
});
