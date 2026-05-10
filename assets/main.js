// Screenshot Interactive — runtime JS
// Reads /data/content.json to set live banner / cine banner / header CTA.

(async function () {
  function $(sel) { return document.querySelector(sel); }
  function show(sel) { var el = $(sel); if (el) el.style.display = 'flex'; }
  function hide(sel) { var el = $(sel); if (el) el.style.display = 'none'; }

  // Hide both banners by default (CSS already does this for #liveBanner, but be safe)
  hide('#liveBanner');
  hide('#cineBanner');
  hide('#stickyPlay');

  var data;
  try {
    var res = await fetch('/data/content.json', { cache: 'no-cache' });
    data = await res.json();
  } catch (e) {
    console.warn('[screenshot] content.json not available — using defaults');
    return;
  }

  var now = new Date();

  // 1. Check live Screen Test event
  var liveEvent = (data.liveEvents || []).find(function (e) {
    if (!e.isLive) return false;
    var s = new Date(e.startTime);
    var en = new Date(e.endTime);
    return s <= now && now <= en;
  });

  // 2. Check Social Cine' tickets
  var nextOnSale = (data.socialCineEditions || [])
    .filter(function (e) { return e.ticketsOnSale && new Date(e.eventDate) >= now; })
    .sort(function (a, b) { return new Date(a.eventDate) - new Date(b.eventDate); })[0];

  // 3. Apply state — live event takes priority over tickets
  if (liveEvent) {
    show('#liveBanner');
    document.body.classList.add('live');
    var t = $('#liveBannerText');
    if (t) t.textContent = '🔴 LIVE NOW — ' + liveEvent.name + ' at ' + liveEvent.venue;
    var cta = $('#headerCta');
    if (cta) {
      cta.textContent = '🔴 Join the live quiz';
      cta.setAttribute('href', '/play');
    }
    show('#stickyPlay');
  } else if (nextOnSale) {
    show('#cineBanner');
    document.body.classList.add('tickets');
    var t2 = $('#cineBannerText');
    if (t2) {
      var d = new Date(nextOnSale.eventDate);
      var months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
      var dateLabel = months[d.getMonth()] + ' ' + d.getDate();
      t2.textContent = '🎬 TICKETS ON SALE — ' + nextOnSale.editionName + ' · ' + dateLabel + ' · ' + (nextOnSale.venue || 'Devon House');
    }
    var cta2 = $('#headerCta');
    if (cta2) {
      var shortName = nextOnSale.editionName.replace(/\s+(Edition|Weekend|Run)$/i, '');
      cta2.textContent = '🎬 Tickets — ' + shortName;
      cta2.setAttribute('href', '/social-cine/schedule');
      cta2.style.background = '#FFC14D';
      cta2.style.color = '#0a0a0a';
    }
  }

  // 4. Highlight active nav link
  var path = location.pathname.replace(/\/$/, '') || '/';
  document.querySelectorAll('.nav-items a[data-page]').forEach(function (a) {
    var p = a.getAttribute('data-page');
    if ((p === 'home' && path === '/') || path.indexOf('/' + p) === 0) a.classList.add('active');
  });

  // 5. data-link attribute for clickable cards (replaces onclick="go()")
  document.querySelectorAll('[data-link]').forEach(function (el) {
    el.style.cursor = 'pointer';
    el.addEventListener('click', function () {
      location.href = el.getAttribute('data-link');
    });
  });
})();
