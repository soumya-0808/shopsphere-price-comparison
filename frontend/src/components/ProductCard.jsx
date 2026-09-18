import {useEffect,useState} from 'react';
import {Link} from 'react-router-dom';
import {motion} from 'framer-motion';
import {Star,TrendingDown,Heart,ExternalLink} from 'lucide-react';
import {isLoggedIn,addServerWishlist,removeServerWishlist} from '../lib/api';
import {openRetailer} from '../lib/offers';
const read=k=>{try{return JSON.parse(localStorage.getItem(k)||'[]')}catch{return[]}};
export default function ProductCard({p,index=0}){
 const sorted=[...(p.prices||[])].sort((a,b)=>a.price-b.price);
 const min=sorted[0]?.price || 0;
 const best=sorted[0];
 const quickOffers=sorted.slice(0,4);
 const [wish,setWish]=useState(read('shopsphere_wishlist').includes(p.id));
 useEffect(()=>{const f=()=>setWish(read('shopsphere_wishlist').includes(p.id));window.addEventListener('shopsphere-storage',f);return()=>window.removeEventListener('shopsphere-storage',f)},[p.id]);
 const toggleWish=async e=>{e.preventDefault();e.stopPropagation();const exists=read('shopsphere_wishlist').includes(p.id);try{if(isLoggedIn()){if(exists)await removeServerWishlist(p.id);else await addServerWishlist(p.id)}}catch{}const ids=read('shopsphere_wishlist');const next=exists?ids.filter(x=>x!==p.id):[...ids,p.id];localStorage.setItem('shopsphere_wishlist',JSON.stringify(next));setWish(!exists);window.dispatchEvent(new Event('shopsphere-storage'));};
 const shop=e=>{e.preventDefault();e.stopPropagation();openRetailer(best?.marketplace,p)};
 return <motion.article className="card product-card" initial={{opacity:0,y:28}} whileInView={{opacity:1,y:0}} viewport={{once:true,margin:'-50px'}} transition={{delay:index*.025,duration:.55}} whileHover={{y:-9}}>
   <Link to={`/products/${p.id}`}><div className="img-wrap"><img loading="lazy" decoding="async" fetchpriority="low" src={p.image_url} alt={p.name} onError={e=>{e.currentTarget.style.opacity=.25}}/><span className="deal"><TrendingDown size={13}/> {Math.max(...p.prices.map(x=>x.discount_pct||0))}% off</span><button className={`heart-float ${wish?'is-wish':''}`} onClick={toggleWish} aria-label="Wishlist"><Heart size={16} fill={wish?'currentColor':'none'}/></button></div><div className="card-body"><div className="eyebrow">{p.brand} · {p.category}</div><h3>{p.name}</h3><div className="rating"><Star size={14} fill="currentColor"/> {p.rating}</div><div className="price-row"><div><strong>₹{min.toLocaleString('en-IN')}</strong><small>lowest offer</small></div><span>at {best?.marketplace}</span></div><div className="offer-count">{p.prices.length} retailer offers · lowest is not fixed to one store</div><div className="retailer-mini-list">{quickOffers.map((o,i)=><span className={i===0?'is-lowest':''} key={o.marketplace}><b>{o.marketplace}</b> ₹{Number(o.price).toLocaleString('en-IN')}</span>)}</div></div></Link>
   <div className="product-actions"><Link className="compare-btn" to={`/products/${p.id}`}>Compare offers</Link><button className="shop-best" onClick={shop}><ExternalLink size={15}/> Shop lowest · {best?.marketplace}</button></div>
 </motion.article>
}
