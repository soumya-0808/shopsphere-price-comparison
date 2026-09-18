const clean = value => String(value || '').trim();
const q = value => encodeURIComponent(clean(value));

// Demo redirect templates. Production should replace these with retailer/affiliate
// deep links supplied by approved feeds or partner APIs for the exact SKU.
export function getRetailerUrl(marketplace, product) {
  const name = product?.name || '';
  const brand = product?.brand || '';
  const query = q(`${brand} ${name}`);
  const map = {
    'Amazon': `https://www.amazon.in/s?k=${query}`,
    'Flipkart': `https://www.flipkart.com/search?q=${query}`,
    'Croma': `https://www.croma.com/search?text=${query}`,
    'Reliance Digital': `https://www.reliancedigital.in/search?q=${query}`,
    'Vijay Sales': `https://www.vijaysales.com/search?searchTerm=${query}`,
    'Tata Neu': `https://www.tataneu.com/search?q=${query}`,
    'Apple Store': 'https://www.apple.com/in/store/',
    'Samsung Shop': 'https://www.samsung.com/in/'
  };
  return map[marketplace] || `https://www.google.com/search?q=${query}`;
}

export function openRetailer(marketplace, product) {
  const url = getRetailerUrl(marketplace, product);
  window.location.assign(url);
}
