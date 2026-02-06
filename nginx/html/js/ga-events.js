(function(){
  const sendEvent = (name, params) => {
    if (typeof gtag === 'function') {
      try { gtag('event', name, params || {}); } catch(e) { console.warn('gtag error', e); }
    }
  };

  const parseResultsCount = () => {
    const info = document.getElementById('resultsInfo');
    if (!info) return null;
    const m = info.innerText.match(/(\d{1,3}(?:[,\d]*)?)/);
    if (m) return parseInt(m[1].replace(/,/g,''),10);
    return null;
  };

  const parsePageNumber = () => {
    const pi = document.getElementById('pageInfo');
    if (!pi) return null;
    const m = pi.innerText.match(/(\d+)/);
    return m? parseInt(m[1],10): null;
  };

  // Search handling (Enter or debounce)
  const searchInput = document.getElementById('searchInput');
  const searchClear = document.getElementById('searchClear');
  let searchDebounce;
  if (searchInput) {
    const sendSearch = (type='debounce')=>{
      const term = searchInput.value.trim().slice(0,200);
      if (!term) return;
      sendEvent('search', {
        search_term: term,
        results_count: parseResultsCount(),
        search_type: type
      });
    };
    searchInput.addEventListener('keydown', (e)=>{
      if (e.key === 'Enter') { sendSearch('enter'); }
    });
    searchInput.addEventListener('input', ()=>{
      clearTimeout(searchDebounce);
      searchDebounce = setTimeout(()=> sendSearch('debounce'), 700);
    });
    if (searchClear) {
      searchClear.addEventListener('click', ()=> {
        searchInput.value = '';
        sendEvent('search', {search_term:'', results_count: parseResultsCount(), search_type: 'clear'});
      });
    }
  }

  // Refresh / update_click
  const refreshBtn = document.getElementById('refreshBtn');
  if (refreshBtn) {
    refreshBtn.addEventListener('click', ()=>{
      sendEvent('update_click',{ item_id: null, update_type: 'refresh', success: true });
    });
  }

  // Sort change
  const sortBy = document.getElementById('sortBy');
  if (sortBy) {
    sortBy.addEventListener('change', ()=>{
      sendEvent('sort_change', { sort_by: sortBy.value, direction: null, results_count: parseResultsCount() });
    });
  }

  // Filters
  document.querySelectorAll('.filter-chip').forEach(btn=>{
    btn.addEventListener('click', ()=>{
      const filterName = btn.dataset.filter || btn.innerText || 'filter';
      sendEvent('filter_apply', { filter_name: filterName, filter_value: filterName, results_count: parseResultsCount() });
    });
  });

  // Pagination
  const prevPage = document.getElementById('prevPage');
  const nextPage = document.getElementById('nextPage');
  [prevPage, nextPage].forEach(btn=>{
    if (!btn) return;
    btn.addEventListener('click', ()=>{
      const page = parsePageNumber();
      sendEvent('paginate', { page_number: page, page_action: btn.id, page_size: null });
    });
  });

  // Delegated clicks for items / external links
  const grid = document.getElementById('subredditGrid');
  if (grid) {
    grid.addEventListener('click', (e)=>{
      const link = e.target.closest('a');
      if (!link) return;
      const href = link.getAttribute('href') || link.dataset.href || null;
      const itemId = link.dataset.itemId || (link.closest('[data-item-id]') && link.closest('[data-item-id]').dataset && link.closest('[data-item-id]').dataset.itemId) || null;
      const isExternal = href && /^(https?:)?\/\//.test(href) && !href.startsWith('/');
      if (isExternal) {
        try{
          sendEvent('click_external', { url: href, domain: (new URL(href)).hostname });
        }catch(e){ sendEvent('click_external', { url: href, domain: null }); }
      } else {
        sendEvent('click_item', { item_id: itemId, destination_url: href });
        sendEvent('view_item', { item_id: itemId, item_category: link.dataset.category || null, position: null });
      }
    });
  }

})();
