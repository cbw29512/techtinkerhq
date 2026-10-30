/* Accessible, network-free browse filtering; DOM is never replaced. */
(() => {
  'use strict';
  try {
    const input = document.getElementById('guide-search');
    const buttons = [...document.querySelectorAll('[data-filter]')];
    const cards = [...document.querySelectorAll('#guides-grid .guide-card')];
    const counter = document.getElementById('result-count');
    const empty = document.getElementById('empty-state');
    if (!input || !counter || !empty || !cards.length) return;
    let currentCategory = 'All';
    function filterGuides() {
      try {
        const query = input.value.trim().toLocaleLowerCase();
        let visible = 0;
        cards.forEach((card) => {
          const categoryMatches = currentCategory === 'All' || card.dataset.category === currentCategory;
          const queryMatches = !query || (card.dataset.search || '').toLocaleLowerCase().includes(query);
          card.hidden = !(categoryMatches && queryMatches);
          if (!card.hidden) visible += 1;
        });
        counter.textContent = `${visible} ${visible === 1 ? 'guide' : 'guides'}`;
        empty.hidden = visible !== 0;
      } catch (error) {
        console.error('Guide filter failed; original guides remain available', error);
        cards.forEach((card) => { card.hidden = false; });
        counter.textContent = 'All guides';
        empty.hidden = true;
      }
    }
    input.addEventListener('input', filterGuides);
    buttons.forEach((button) => button.addEventListener('click', () => {
      currentCategory = button.dataset.filter;
      buttons.forEach((b) => {
        b.classList.toggle('active', b === button);
        b.setAttribute('aria-pressed', String(b === button));
      });
      filterGuides();
    }));
  } catch (error) {
    console.error('Could not initialize guide filter', error);
  }
})();
