import {Link,useNavigate,useLocation} from 'react-router-dom';
import {Heart,Sparkles,LogOut,Menu,X,Bell} from 'lucide-react';
import {motion} from 'framer-motion';
import {useEffect,useState} from 'react';
function count(key){try{return JSON.parse(localStorage.getItem(key)||'[]').length}catch{return 0}}
function alertCount(){try{return Object.keys(localStorage).filter(k=>k.startsWith('alert_')).length}catch{return 0}}
export default function Navbar(){
 const nav=useNavigate(),loc=useLocation(),[open,setOpen]=useState(false),[logged,setLogged]=useState(!!localStorage.getItem('shopsphere_token')),[wish,setWish]=useState(count('shopsphere_wishlist')),[alerts,setAlerts]=useState(alertCount());
 const refresh=()=>{setWish(count('shopsphere_wishlist'));setAlerts(alertCount());setLogged(!!localStorage.getItem('shopsphere_token'));};
 useEffect(()=>{refresh();window.addEventListener('shopsphere-storage',refresh);window.addEventListener('shopsphere-auth',refresh);window.addEventListener('shopsphere-alerts',refresh);return()=>{window.removeEventListener('shopsphere-storage',refresh);window.removeEventListener('shopsphere-auth',refresh);window.removeEventListener('shopsphere-alerts',refresh)}},[loc.pathname]);
 const logout=()=>{localStorage.removeItem('shopsphere_token');setLogged(false);nav('/');window.dispatchEvent(new Event('shopsphere-auth'));};
 const links=[['Explore','/products'],['Laptops','/products?category=Laptops'],['Phones','/products?category=Smartphones'],['Audio','/products?category=Audio'],['Gaming','/products?category=Gaming']];
 return <motion.header initial={{y:-70,opacity:0}} animate={{y:0,opacity:1}} className="nav"><Link className="brand" to="/" onClick={()=>setOpen(false)}><motion.span className="brandmark" whileHover={{rotate:10,scale:1.08}}><Sparkles size={17}/></motion.span>ShopSphere</Link>
  <nav className={open?'mobile-open':''}>{links.map(([label,to])=><Link key={label} to={to} onClick={()=>setOpen(false)} className={loc.pathname==='/products'&&to===loc.pathname?'active-nav':''}>{label}</Link>)}</nav>
  <div className="nav-actions"><Link className="count-link" to="/alerts" aria-label="Price alerts"><Bell size={19}/>{alerts>0&&<b>{alerts}</b>}</Link>{logged?<button className="icon-btn" title="Sign out" onClick={logout}><LogOut size={18}/></button>:<Link className="login-link" to="/login">Sign in</Link>}<button className="menu-btn" onClick={()=>setOpen(!open)} aria-label="Menu">{open?<X/>:<Menu/>}</button></div>
 </motion.header>
}
