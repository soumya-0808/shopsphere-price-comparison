import axios from 'axios';

export const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';
export const api = axios.create({baseURL: API_URL, timeout: 4000});

// Small in-memory cache keeps browser-back/navigation fast without persisting stale catalog data.
const cache = new Map();
const cachedGet = async (key, request, ttl = 30000) => {
  const hit = cache.get(key);
  if (hit && (Date.now() - hit.time) < ttl) return hit.data;
  const data = await request();
  cache.set(key, {time: Date.now(), data});
  return data;
};
api.interceptors.request.use(config=>{const token=localStorage.getItem('shopsphere_token');if(token)config.headers.Authorization=`Bearer ${token}`;return config;});
api.interceptors.response.use(r=>r,error=>{if(error.response?.status===401&&localStorage.getItem('shopsphere_token')){localStorage.removeItem('shopsphere_token');window.dispatchEvent(new Event('shopsphere-auth'));}return Promise.reject(error);});
export const isLoggedIn=()=>!!localStorage.getItem('shopsphere_token');
export async function getProducts(params={}){const key=`products:${JSON.stringify(params)}`;return cachedGet(key,async()=>{const r=await api.get('/products',{params});return Array.isArray(r.data)?r.data:[];},60000);}
export async function getProduct(id){return cachedGet(`product:${id}`,async()=>{const r=await api.get(`/products/${id}`);return r.data;},120000);}
export async function getHistory(id,marketplace){const key=`history:${id}:${marketplace||'all'}`;return cachedGet(key,async()=>{const r=await api.get(`/products/${id}/history`,{params:marketplace?{marketplace}:{}});return Array.isArray(r.data)?r.data:[];},120000);}
export async function getMeta(){return cachedGet('meta',async()=>{const r=await api.get('/products/meta/categories');return r.data||{categories:[],brands:[],marketplaces:[]};},60000);}
export async function serverWishlist(){const r=await api.get('/me/wishlist');return r.data;}
export async function addServerWishlist(id){return api.post(`/me/wishlist/${id}`);}
export async function removeServerWishlist(id){return api.delete(`/me/wishlist/${id}`);}
export async function createPriceAlert(product_id,min_price,max_price){return api.post('/me/price-alerts',{product_id,min_price,max_price,target_price:min_price});}
export async function getPriceAlerts(){const r=await api.get('/me/price-alerts');return Array.isArray(r.data)?r.data:[];}
export async function getGuestPriceAlerts(){
  const keys=Object.keys(localStorage).filter(k=>k.startsWith('alert_'));
  const ids=keys.map(k=>Number(k.slice(6))).filter(Number.isFinite);
  if(!ids.length)return [];
  const products=await Promise.all(ids.map(id=>getProduct(id).catch(()=>null)));
  return products.filter(Boolean).map(p=>{
    const raw=localStorage.getItem(`alert_${p.id}`);
    let cfg={}; try{cfg=JSON.parse(raw||'{}')}catch{}
    const prices=Array.isArray(p.prices)?p.prices:[];
    const best=prices.length?prices.reduce((a,b)=>a.price<b.price?a:b):null;
    const min=Number(cfg.min||0), max=Number(cfg.max||0);
    return {id:`guest-${p.id}`, product_id:p.id, product_name:p.name, brand:p.brand, image_url:p.image_url, min_price:min, max_price:max, current_price:best?.price||null, marketplace:best?.marketplace||'', active:cfg.active !== false, triggered:cfg.triggered === true, in_range_now:!!best&&min<=best.price&&best.price<=max, guest:true};
  });
}
export function deleteGuestPriceAlert(productId){localStorage.removeItem(`alert_${productId}`);window.dispatchEvent(new Event('shopsphere-alerts'));}
export async function checkPriceAlerts(){const r=await api.get('/me/price-alerts/check');return r.data?.triggered||[];}
export async function markAlertSeen(id){return api.post(`/me/price-alerts/${id}/seen`);}
export async function reactivatePriceAlert(id){return api.post(`/me/price-alerts/${id}/reactivate`);}
export async function deletePriceAlert(id){return api.delete(`/me/price-alerts/${id}`);}
