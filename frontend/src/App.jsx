import {Component, lazy, Suspense, useEffect, useState} from 'react';
import {BrowserRouter, Routes, Route, useLocation} from 'react-router-dom';
import Navbar from './components/Navbar';
const Home = lazy(() => import('./pages/Home'));
const Products = lazy(() => import('./pages/Products'));
const ProductDetail = lazy(() => import('./pages/ProductDetail'));
const Auth = lazy(() => import('./pages/Auth'));
const Wishlist = lazy(() => import('./pages/Wishlist'));
const Alerts = lazy(() => import('./pages/Alerts'));
import {checkPriceAlerts,markAlertSeen,isLoggedIn} from './lib/api';
import {Bell,X} from 'lucide-react';
import {motion} from 'framer-motion';

class AppErrorBoundary extends Component {
  state = {error: null};
  static getDerivedStateFromError(error){ return {error}; }
  render(){
    if(!this.state.error) return this.props.children;
    return <section className="fatal-error">
      <div className="empty-icon">!</div>
      <div className="eyebrow">SHOPSPHERE RECOVERY</div>
      <h1>That view hit an unexpected error.</h1>
      <p>The app is still running. Try returning to the catalog or refreshing this page.</p>
      <div className="fatal-actions">
        <button className="primary" onClick={()=>window.location.assign('/')}>Return home</button>
        <button className="secondary" onClick={()=>window.location.reload()}>Refresh</button>
      </div>
      <small>{this.state.error?.message || 'Unknown client error'}</small>
    </section>;
  }
}

function ScrollToTop(){
  const {pathname, search} = useLocation();
  useEffect(()=>{ window.scrollTo({top:0,left:0,behavior:'auto'}); },[pathname,search]);
  return null;
}

function PriceAlertWatcher(){
  const [hit,setHit]=useState(null);
  useEffect(()=>{
    let timer;
    const notify=async item=>{
      setHit(item); setTimeout(()=>setHit(null),9000);
      if('Notification' in window && Notification.permission==='granted') new Notification(`Price target reached: ${item.product_name}`,{body:`${item.marketplace} has the lowest offer at ₹${Number(item.current_price).toLocaleString('en-IN')} — inside your ₹${Number(item.min_price).toLocaleString('en-IN')}–₹${Number(item.max_price).toLocaleString('en-IN')} target.`,tag:`shopsphere-${item.id}`});
      if(isLoggedIn()) try{await markAlertSeen(item.id)}catch{}
    };
    const run=async()=>{
      if(isLoggedIn()){
        try{const hits=await checkPriceAlerts();for(const item of hits) await notify(item);}catch{}
      }
      // Guest alerts are kept locally; this gives them a browser/in-app hit while the site is open.
      const keys=Object.keys(localStorage).filter(k=>k.startsWith('alert_'));
      for(const key of keys){try{const cfg=JSON.parse(localStorage.getItem(key));const id=Number(key.replace('alert_',''));if(!id||!cfg?.min||!cfg?.max||cfg.active===false)continue;const product=await (await fetch(`${import.meta.env.VITE_API_URL||'http://localhost:8000/api'}/products/${id}`)).json();const prices=product?.prices||[];if(!prices.length)continue;const best=prices.reduce((a,b)=>a.price<b.price?a:b);if(best.price>=Number(cfg.min)&&best.price<=Number(cfg.max)){await notify({id:`guest-${id}`,current_price:best.price,min_price:cfg.min,max_price:cfg.max,product_name:product.name,marketplace:best.marketplace});localStorage.setItem(key,JSON.stringify({...cfg,active:false,triggered:true,triggeredAt:new Date().toISOString()}));}}catch{}}
    };
    const first=setTimeout(run,5000); timer=setInterval(run,60000); return()=>{clearTimeout(first);clearInterval(timer)};
  },[]);
  if(!hit)return null;
  return <motion.div className="price-hit-notice" initial={{opacity:0,x:40,y:-15}} animate={{opacity:1,x:0,y:0}} exit={{opacity:0,x:40}}><div className="hit-icon"><Bell size={17}/></div><div><div className="eyebrow">PRICE TARGET REACHED</div><b>{hit.product_name}</b><span>{hit.marketplace} · ₹{Number(hit.current_price).toLocaleString('en-IN')} is inside your target range</span></div><button onClick={()=>setHit(null)}><X size={15}/></button></motion.div>;
}

function Shell(){
  return <>
    <ScrollToTop/>
    <PriceAlertWatcher/>
    <Navbar/>
    <main><Suspense fallback={<div className="route-loading"><div className="loader"/>Loading ShopSphere…</div>}><Routes>
      <Route path="/" element={<Home/>}/>
      <Route path="/products" element={<Products/>}/>
      <Route path="/products/:id" element={<ProductDetail/>}/>
      <Route path="/login" element={<Auth/>}/>
      <Route path="/wishlist" element={<Wishlist/>}/>
      <Route path="/alerts" element={<Alerts/>}/>
      <Route path="*" element={<Products/>}/>
    </Routes></Suspense></main>
    <footer><span>ShopSphere</span> · Price intelligence demo · React + FastAPI + PostgreSQL</footer>
  </>;
}

export default function App(){
  return <BrowserRouter><AppErrorBoundary><Shell/></AppErrorBoundary></BrowserRouter>;
}
