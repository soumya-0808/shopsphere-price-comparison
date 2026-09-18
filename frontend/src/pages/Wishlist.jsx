import {useEffect,useState} from 'react';
import {Link} from 'react-router-dom';
import {getProducts,isLoggedIn,serverWishlist,removeServerWishlist} from '../lib/api';
import ProductCard from '../components/ProductCard';
import {Heart,ArrowRight,RefreshCw} from 'lucide-react';
const read=()=>{try{return JSON.parse(localStorage.getItem('shopsphere_wishlist')||'[]')}catch{return[]}};
export default function Wishlist(){
 const [products,setProducts]=useState([]),[loading,setLoading]=useState(true),[error,setError]=useState('');
 const load=async()=>{setLoading(true);setError('');try{if(isLoggedIn()){const server=await serverWishlist();const ids=server.map(p=>p.id);localStorage.setItem('shopsphere_wishlist',JSON.stringify(ids));setProducts(server)}else{const ids=read();const all=await getProducts();setProducts(all.filter(p=>ids.includes(p.id)))}}catch(e){setError('Could not load your wishlist.');}finally{setLoading(false)}};
 useEffect(()=>{load();const f=()=>load();window.addEventListener('shopsphere-storage',f);return()=>window.removeEventListener('shopsphere-storage',f)},[]);
 const remove=async id=>{try{if(isLoggedIn())await removeServerWishlist(id)}catch{}const ids=read().filter(x=>x!==id);localStorage.setItem('shopsphere_wishlist',JSON.stringify(ids));window.dispatchEvent(new Event('shopsphere-storage'));setProducts(v=>v.filter(p=>p.id!==id));};
 return <section className="section"><div className="section-head"><div><div className="eyebrow">SAVED FOR LATER</div><h1>Your wishlist</h1><p className="muted">Keep products you are watching in one place.</p></div><Heart className="section-icon"/></div>
 {loading?<div className="loading small-loading"><div className="loader"/>Loading wishlist…</div>:error?<div className="empty"><div className="empty-icon">!</div><h2>{error}</h2><button className="primary" onClick={load}><RefreshCw size={15}/> Retry</button></div>:products.length?<div className="grid">{products.map((p,i)=><div key={p.id} className="wishlist-item"><ProductCard p={p} index={i}/><button className="wishlist-remove" onClick={()=>remove(p.id)}>Remove from wishlist</button></div>)}</div>:<div className="empty"><div className="empty-icon"><Heart/></div><h2>Your wishlist is empty</h2><p>Tap the heart on any product to save it here.</p><Link className="primary" to="/products">Explore electronics <ArrowRight size={16}/></Link></div>}
 </section>
}
