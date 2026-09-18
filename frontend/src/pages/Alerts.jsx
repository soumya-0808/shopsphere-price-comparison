import {useEffect,useState} from 'react';
import {Link,useNavigate} from 'react-router-dom';
import {Bell,CheckCircle2,Trash2,RefreshCw,ShieldCheck,ArrowRight,UserRound,ArrowLeft} from 'lucide-react';
import {deletePriceAlert,getPriceAlerts,getGuestPriceAlerts,deleteGuestPriceAlert,isLoggedIn,reactivatePriceAlert} from '../lib/api';
import {motion} from 'framer-motion';

const money=n=>`₹${Number(n||0).toLocaleString('en-IN')}`;
export default function Alerts(){
 const nav=useNavigate();
 const [alerts,setAlerts]=useState([]),[loading,setLoading]=useState(true),[error,setError]=useState('');
 const [notificationState,setNotificationState]=useState(()=>('Notification' in window?Notification.permission:'unsupported'));
 const [notificationMessage,setNotificationMessage]=useState('');
 const logged=isLoggedIn();
 const load=async()=>{setLoading(true);setError('');try{
   const guest=await getGuestPriceAlerts();
   if(logged){
     try{const server=await getPriceAlerts();setAlerts([...server,...guest.filter(g=>!server.some(s=>s.product_id===g.product_id))]);}
     catch{setAlerts(guest);setError(guest.length?'Your synced alerts could not be loaded, so your local alerts are shown.':'Could not load synced alerts.');}
   } else setAlerts(guest);
 }catch{setError('Could not load your price alerts.')}finally{setLoading(false)}};
 useEffect(()=>{load();const refresh=()=>load();window.addEventListener('shopsphere-alerts',refresh);window.addEventListener('shopsphere-auth',refresh);return()=>{window.removeEventListener('shopsphere-alerts',refresh);window.removeEventListener('shopsphere-auth',refresh)}},[]);
 const remove=async a=>{try{if(a.guest)deleteGuestPriceAlert(a.product_id);else await deletePriceAlert(a.id);setAlerts(v=>v.filter(x=>x.id!==a.id));}catch{setError('Could not remove this alert.');}};
 const rearm=async a=>{try{if(a.guest){const raw=JSON.parse(localStorage.getItem(`alert_${a.product_id}`)||'{}');localStorage.setItem(`alert_${a.product_id}`,JSON.stringify({...raw,active:true,triggered:false}));window.dispatchEvent(new Event('shopsphere-alerts'));}else await reactivatePriceAlert(a.id);await load();}catch{setError('Could not reactivate this alert.');}};
 const ask=async()=>{
   if(!('Notification' in window)){setNotificationState('unsupported');setNotificationMessage('This browser does not support desktop notifications.');return;}
   try{
     const permission=Notification.permission==='default'?await Notification.requestPermission():Notification.permission;
     setNotificationState(permission);
     if(permission==='granted'){
       new Notification('ShopSphere notifications enabled',{body:'Price-hit notifications are now enabled.'});
       setNotificationMessage('Notifications are enabled. A test notification was sent.');
     }else if(permission==='denied'){
       setNotificationMessage('Notifications are blocked for localhost. Open Chrome Site settings → Notifications → Allow, then reload this page.');
     }else{
       setNotificationMessage('Notification permission was not granted.');
     }
   }catch{setNotificationMessage('Could not request notification permission. Check Chrome site settings.');}
 };
 const testNotification=()=>{
   if(!('Notification' in window)||Notification.permission!=='granted'){ask();return;}
   new Notification('ShopSphere test notification',{body:'Your browser is ready for price-hit alerts.'});
   setNotificationMessage('Test notification sent successfully.');
 };
 const goBack=()=>{if(window.history.length>1)nav(-1);else nav('/products')};
 return <section className="section alerts-page">
  <motion.button className="back-button alerts-back" whileHover={{x:-5,scale:1.02}} whileTap={{scale:.96}} onClick={goBack}><ArrowLeft size={16}/> Back</motion.button>
  <div className="section-head"><div><div className="eyebrow">PRICE WATCHLIST</div><h1>Your price alerts</h1><p className="muted">Set a range, then ShopSphere watches the lowest comparison offer. When the price enters your range, the alert fires once and pauses until you reactivate it.</p></div><Bell className="section-icon"/></div>
  {!logged&&<div className="notification-permission"><span><UserRound size={15}/> Guest alerts are saved on this browser. Sign in to sync them across sessions and devices.</span><div className="notification-actions"><button onClick={notificationState==='granted'?testNotification:ask}>{notificationState==='granted'?'Test notification':notificationState==='denied'?'Check notification access':'Enable notifications'}</button>{notificationState==='granted'&&<span className="notification-state">● Ready</span>}<Link className="primary" to="/login">Sign in / Create account <ArrowRight size={15}/></Link></div></div>}
  {logged&&<div className="notification-permission"><span><ShieldCheck size={15}/> Allow browser notifications for instant price-hit alerts while the app is open.</span><div className="notification-actions"><button onClick={notificationState==='granted'?testNotification:ask}>{notificationState==='granted'?'Test notification':notificationState==='denied'?'Check notification access':'Enable notifications'}</button>{notificationState==='granted'&&<span className="notification-state">● Ready</span>}</div></div>}
  {notificationMessage&&<div className={'alert-inline-warning notification-feedback '+(notificationState==='granted'?'notification-ok':'')}>{notificationMessage}</div>}
  {loading?<div className="loading small-loading"><div className="loader"/>Loading alerts…</div>:error&&!alerts.length?<div className="empty"><div className="empty-icon">!</div><h2>{error}</h2><button className="primary" onClick={load}><RefreshCw size={15}/> Retry</button></div>:alerts.length?<>
   {error&&<div className="alert-inline-warning">{error}</div>}
   <div className="alert-grid">{alerts.map(a=><article className="alert-card" key={a.id}><img src={a.image_url} alt=""/><div><div className="eyebrow">{a.brand}</div><h3>{a.product_name}</h3><div className="alert-meta">Target range: {money(a.min_price)} – {money(a.max_price)}</div><div className="alert-price"><b>{money(a.current_price)}</b><span className="alert-range">current lowest{a.marketplace?` · ${a.marketplace}`:''}</span></div>{a.triggered?<div className="alert-hit"><CheckCircle2 size={12}/> Target reached · alert paused</div>:a.active&&<div className="alert-active"><Bell size={12}/> Active · checking for a range hit</div>}<div className="alert-actions"><Link to={`/products/${a.product_id}`}>Open product</Link>{!a.active&&<button onClick={()=>rearm(a)}><Bell size={13}/> Reactivate</button>}<button onClick={()=>remove(a)}><Trash2 size={13}/> Remove</button></div></div></article>)}</div>
  </>:<div className="empty"><div className="empty-icon"><Bell/></div><h2>No price alerts yet</h2><p>Open any product, choose <b>Set price alert</b>, and enter the price range you want.</p><Link className="primary" to="/products">Explore products</Link></div>}
 </section>
}
