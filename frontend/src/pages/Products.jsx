import {useEffect,useMemo,useState} from 'react';
import {useSearchParams} from 'react-router-dom';
import {getProducts,getMeta} from '../lib/api';
import ProductCard from '../components/ProductCard';
import {SlidersHorizontal,Grid3X3,ListFilter,Search,Boxes,RefreshCw,ArrowLeft} from 'lucide-react';
import {motion} from 'framer-motion';

export default function Products(){
 const [sp,setSp]=useSearchParams();
 const [products,setProducts]=useState([]),[meta,setMeta]=useState({categories:[],brands:[],brands_by_category:{}});
 const [loading,setLoading]=useState(true),[error,setError]=useState('');
 const q=sp.get('q')||''; const category=sp.get('category')||''; const brand=sp.get('brand')||''; const sort=sp.get('sort')||'featured';
 const [draftQ,setDraftQ]=useState(q); const [view,setView]=useState('grid');
 useEffect(()=>{setDraftQ(q)},[q]);

 useEffect(()=>{let alive=true;getMeta().then(data=>alive&&setMeta(data)).catch(()=>{});return()=>{alive=false}},[]);
 useEffect(()=>{let alive=true;setLoading(true);setError('');getProducts({q:q||undefined,category:category||undefined,brand:brand||undefined,sort,limit:100}).then(data=>{if(alive)setProducts(data)}).catch(()=>{if(alive){setProducts([]);setError('We could not load this catalog view. Please retry.')}}).finally(()=>alive&&setLoading(false));return()=>{alive=false}},[q,category,brand,sort]);
 const update=(key,value)=>{const next=new URLSearchParams(sp);if(value)next.set(key,value);else next.delete(key);setSp(next)};
 useEffect(()=>{ if(!brand||!category) return; const map=meta.brands_by_category||{}; const key=Object.keys(map).find(k=>k.toLowerCase()===category.toLowerCase()); if(key && !map[key].some(b=>b.toLowerCase()===brand.toLowerCase())) update('brand',''); },[category,brand,meta.brands_by_category]);
 const submitSearch=e=>{e.preventDefault();update('q',draftQ.trim())};
 const reset=()=>setSp({});
 const visibleBrands=useMemo(()=>{ const map=meta.brands_by_category||{}; if(category){ const key=Object.keys(map).find(k=>k.toLowerCase()===category.toLowerCase()); return (key?map[key]:[]).slice().sort(); } return (meta.brands||[]).slice().sort(); },[meta,category]);
 return <section className="section products-page">
  <motion.button className="back-button" whileHover={{x:-5,scale:1.02}} whileTap={{scale:.96}} onClick={()=>window.history.length>1?window.history.back():window.location.assign('/')}><ArrowLeft size={16}/> Back</motion.button>
  <div className="catalog-hero"><div><div className="eyebrow">DISCOVER / {loading?'…':products.length} RESULTS</div><h1>{q?`Results for “${q}”`:(category||'Shop electronics')}</h1><p className="muted">Browse brands and specific products, then compare retailer offers before choosing where to buy.</p></div><div className="catalog-stat"><Boxes/><strong>{meta.categories?.length||0}</strong><span>categories</span></div></div>
  <form className="toolbar" onSubmit={submitSearch}><div className="search-filter"><Search size={17}/><input value={draftQ} onChange={e=>setDraftQ(e.target.value)} placeholder="Search products, brands, categories..."/><button className="search-submit" aria-label="Search" type="submit"><Search size={15}/></button></div><select value={category} onChange={e=>update('category',e.target.value)}><option value="">All categories</option>{meta.categories?.map(c=><option key={c} value={c}>{c}</option>)}</select><select value={brand} onChange={e=>update('brand',e.target.value)}><option value="">All brands{category?' in this category':''}</option>{visibleBrands.map(b=><option key={b} value={b}>{b}</option>)}</select><select value={sort} onChange={e=>update('sort',e.target.value)}><option value="featured">Featured</option><option value="rating">Top rated</option><option value="newest">Newest</option></select><div className="view-toggle"><button type="button" className={view==='grid'?'active':''} onClick={()=>setView('grid')}><Grid3X3 size={16}/></button><button type="button" className={view==='list'?'active':''} onClick={()=>setView('list')}><ListFilter size={16}/></button></div></form>
  {!loading&&visibleBrands.length>0&&<div className="brand-strip"><span>Brands in this view</span>{visibleBrands.map(b=><button type="button" key={b} className={brand===b?'active':''} onClick={()=>update('brand',brand===b?'':b)}>{b}</button>)}</div>}
  {error&&<div className="inline-error"><span>{error}</span><button onClick={()=>setSp(new URLSearchParams(sp))}><RefreshCw size={15}/> Retry</button></div>}
  {loading?<div className="skeleton-grid">{Array.from({length:12}).map((_,i)=><div className="skeleton-card" key={i}><div/><span/><span/><span/></div>)}</div>:<>{<div className={view==='grid'?'grid':'product-list'}>{products.map((p,i)=><ProductCard key={`${p.id}-${p.name}`} p={p} index={i}/>)}</div>}{!products.length&&!error&&<div className="empty"><div className="empty-icon"><SlidersHorizontal/></div><h2>No products found</h2><p>Try a broader product name, brand, or category.</p><button className="primary" onClick={reset}>Reset filters</button></div>}</>}
 </section>
}
