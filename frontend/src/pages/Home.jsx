import {useEffect,useState} from 'react';
import {Link,useNavigate} from 'react-router-dom';
import {motion} from 'framer-motion';
import {ArrowRight,Search,ShieldCheck,Zap,Sparkles,TrendingDown,ShoppingBag,Activity,Boxes} from 'lucide-react';
import {getProducts,getMeta} from '../lib/api';
import ProductCard from '../components/ProductCard';

export default function Home(){
 const [products,setProducts]=useState([]),[q,setQ]=useState(''),[meta,setMeta]=useState({categories:[]}),[loading,setLoading]=useState(true),[error,setError]=useState('');
 const [videoReady,setVideoReady]=useState(false);
 const navigate=useNavigate();
 useEffect(()=>{let alive=true;getProducts({limit:8}).then(p=>alive&&setProducts(p)).catch(()=>alive&&setError('Catalog is temporarily unavailable.')).finally(()=>alive&&setLoading(false));getMeta().then(m=>alive&&setMeta(m)).catch(()=>{});return()=>{alive=false}},[]);
 const featured=products.slice(0,8);
 const search=e=>{e.preventDefault();navigate(`/products${q.trim()?`?q=${encodeURIComponent(q.trim())}`:''}`)};
 return <>
  <section className="hero cinematic">
   <div className="video-overlay"/><div className="orb orb1"/><div className="orb orb2"/>
   <div className="hero-copy"><motion.div initial={{opacity:0,y:18}} animate={{opacity:1,y:0}} className="pill"><Sparkles size={14}/> Intelligent shopping · multi-store comparison</motion.div>
    <motion.h1 initial={{opacity:0,y:25}} animate={{opacity:1,y:0}} transition={{delay:.1}}>Find the right product.<br/><span>Pay the right price.</span></motion.h1>
    <motion.p initial={{opacity:0}} animate={{opacity:1}} transition={{delay:.25}}>Search electronics, compare retailers, study price movement, save a shortlist and jump directly to the retailer offering you choose.</motion.p>
    <form className="hero-search" onSubmit={search}><Search size={20}/><input value={q} onChange={e=>setQ(e.target.value)} placeholder="Search phones, laptops, TVs, cameras..."/><button type="submit" aria-label="Search"><ArrowRight/></button></form>
    <div className="trust"><span><ShieldCheck size={16}/> Secure account flows</span><span><Zap size={16}/> Price alerts</span><span><Activity size={16}/> History charts</span></div>
   </div>
   <motion.div className="hero-card" initial={{opacity:0,scale:.88,rotate:3}} animate={{opacity:1,scale:1,rotate:0}} transition={{delay:.18,duration:.9}}>
    <div className="floating-tag">PRICE INTELLIGENCE / DEMO</div><div className="live-dot"><i/> Updating comparison</div>
    <div className="mock-product"><div className="mock-image"><img loading="lazy" decoding="async" src={products[2]?.image_url || 'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=800'} /></div><div><small>BEST VALUE</small><h3>{products[2]?.name||'MacBook Air M5'}</h3><div className="mock-price">₹{(products[2] ? Math.min(...products[2].prices.map(x=>x.price)) : 114999).toLocaleString('en-IN')}</div><div className="mini-bars"><i/><i/><i/><i/><i/><i/></div></div></div>
    {products[2]&&<div className="compare">{[...(products[2].prices||[])].sort((a,b)=>a.price-b.price).slice(0,3).map((o,i)=><span key={o.marketplace}>{o.marketplace} <b>₹{Number(o.price).toLocaleString('en-IN')}</b></span>)}<em>Lowest first · choose any retailer</em></div>}
   </motion.div>
  </section>
  <div className="category-marquee"><div>{[...(meta.categories||[]),...(meta.categories||[])].map((c,i)=><Link key={`${c}-${i}`} to={`/products?category=${encodeURIComponent(c)}`}>{c}<span>↗</span></Link>)}</div></div>
  <section className="section"><div className="section-head"><div><div className="eyebrow">Explore the catalog</div><h2>Electronics, without the guesswork</h2><p className="muted">Phones, laptops, tablets, audio, wearables, TVs, cameras, gaming, storage, networking and accessories.</p></div><Link to="/products" className="text-link">View all products <ArrowRight size={16}/></Link></div>
   {error?<div className="empty"><div className="empty-icon"><Boxes/></div><h2>Catalog unavailable</h2><p>{error}</p><button className="primary" onClick={()=>window.location.reload()}>Retry</button></div>:loading?<div className="skeleton-grid">{Array.from({length:8}).map((_,i)=><div className="skeleton-card" key={i}><div/><span/><span/><span/></div>)}</div>:<div className="grid">{featured.map((p,i)=><ProductCard key={`${p.id}-${p.name}`} p={p} index={i}/>)}</div>}
  </section>
  <section className="section value-section"><div className="eyebrow">Built for modern shopping</div><h2>From discovery to decision.</h2><p className="muted journey-lead">A product moves through three clear moments: discover it, understand its market, then choose the offer that fits your target.</p><div className="feature-journey">
    {[{n:'01',icon:TrendingDown,title:'Discover & compare',text:'Search a product and see competing retailer offers together, with the lowest offer and nearby alternatives visible at a glance.'},{n:'02',icon:Activity,title:'Read the price story',text:'Inspect marketplace history, current ranges and movement signals before deciding whether the price is worth acting on.'},{n:'03',icon:ShoppingBag,title:'Choose & shop',text:'Pick a retailer, set a target alert if you want to wait, then continue to the retailer for checkout.'}].map(({n,icon:Icon,title,text},i)=><motion.div className="journey-step" key={n} initial={{opacity:0,y:45,scale:.96}} whileInView={{opacity:1,y:0,scale:1}} viewport={{once:true,amount:.35}} transition={{duration:.65,delay:i*.16,ease:[.22,1,.36,1]}} whileHover={{y:-8}}><div className="journey-line"/><div className="journey-number">{n}</div><motion.div className="journey-icon" whileHover={{rotate:[0,-8,8,0],scale:1.12}} transition={{duration:.45}}><Icon/></motion.div><h3>{title}</h3><p>{text}</p><span className="journey-pulse"/></motion.div>)}
  </div></section>
 </>
}
