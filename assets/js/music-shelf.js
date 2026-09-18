(() => {
  'use strict';
  for (const image of document.querySelectorAll('.cover-frame img')) {
    const missing = () => { image.hidden = true; image.closest('.cover-frame').classList.add('is-missing'); };
    image.addEventListener('error', missing);
    if (image.complete && image.naturalWidth === 0) missing();
  }
  const input = document.getElementById('record-search');
  if (!input) return;
  const cards = [...document.querySelectorAll('[data-record]')];
  const normalize = (text) => String(text).normalize('NFKC').toLocaleLowerCase().trim();
  const filter = () => {
    const words = normalize(input.value).split(/\s+/).filter(Boolean);
    let count = 0;
    for (const card of cards) {
      const text = normalize(card.dataset.search);
      card.hidden = !words.every((word) => text.includes(word));
      if (!card.hidden) count++;
    }
    document.getElementById('search-status').textContent = `${count} 首收藏`;
    document.getElementById('search-empty').hidden = count !== 0;
  };
  input.addEventListener('input', filter);
  const query = new URLSearchParams(location.search).get('q');
  if (query) { input.value = query; filter(); }
})();
