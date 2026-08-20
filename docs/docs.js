// docs.js — sidebar toggle + nav filter
function toggleSidebar() {
  document.querySelector('.wy-nav-side').classList.toggle('open');
}

function filterNav(q) {
  const links = document.querySelectorAll('.wy-menu-vertical li');
  links.forEach(li => {
    const txt = li.textContent.toLowerCase();
    li.classList.toggle('nav-hidden', q.length > 0 && !txt.includes(q.toLowerCase()));
  });
}

// Mark current page in sidebar
(function markCurrentPage() {
  const path = window.location.pathname.split('/').pop() || 'index.html';
  document.querySelectorAll('.wy-menu-vertical ul li a').forEach(a => {
    const href = a.getAttribute('href');
    if (href === path) {
      a.parentElement.classList.add('current');
    }
  });
})();
