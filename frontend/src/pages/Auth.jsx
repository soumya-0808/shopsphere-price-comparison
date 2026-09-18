import {useState} from 'react';
import {useNavigate,useLocation} from 'react-router-dom';
import {api,addServerWishlist} from '../lib/api';
import {motion,AnimatePresence} from 'framer-motion';
import {ShieldCheck,ArrowRight,Sparkles,LockKeyhole,CheckCircle2,Eye,EyeOff,UserRound,Mail,KeyRound} from 'lucide-react';

const readIds=k=>{try{return JSON.parse(localStorage.getItem(k)||'[]')}catch{return[]}};
export default function Auth(){
 const [mode,setMode]=useState('login'),[name,setName]=useState(''),[email,setEmail]=useState(''),[password,setPassword]=useState(''),[confirm,setConfirm]=useState(''),[show,setShow]=useState(false),[busy,setBusy]=useState(false),[error,setError]=useState('');
 const nav=useNavigate(),loc=useLocation();
 async function submit(e){e.preventDefault();setError('');if(mode==='register'&&password!==confirm){setError('Passwords do not match.');return}setBusy(true);try{
   if(mode==='register'){await api.post('/auth/register',{name:name.trim(),email:email.trim().toLowerCase(),password});}
   const body=new URLSearchParams({username:email.trim().toLowerCase(),password});const r=await api.post('/auth/login',body);localStorage.setItem('shopsphere_token',r.data.access_token);window.dispatchEvent(new Event('shopsphere-auth'));
   // Merge the guest wishlist into the authenticated account.
   for(const id of readIds('shopsphere_wishlist')){try{await addServerWishlist(id)}catch{}}
   // Merge guest price ranges into the signed-in account, then keep local copies for offline visibility.
   for(const key of Object.keys(localStorage).filter(k=>k.startsWith('alert_'))){try{const productId=Number(key.slice(6));const cfg=JSON.parse(localStorage.getItem(key)||'{}');if(productId&&cfg.min&&cfg.max) await api.post('/me/price-alerts',{product_id:productId,min_price:Number(cfg.min),max_price:Number(cfg.max),target_price:Number(cfg.min)});}catch{}}
   window.dispatchEvent(new Event('shopsphere-alerts'));
   nav(loc.state?.from||'/',{replace:true});
 }catch(err){setError(err.response?.data?.detail||'Something went wrong. Please try again.')}finally{setBusy(false)}}
 const switchMode=()=>{setMode(v=>v==='login'?'register':'login');setError('');setConfirm('');};
 return <section className="auth-page">
  <div className="auth-aurora aurora-a"/><div className="auth-aurora aurora-b"/>
  <div className="auth-art">
   <motion.div className="auth-orbit" animate={{rotate:360}} transition={{duration:18,repeat:Infinity,ease:'linear'}}><span/><span/><span/></motion.div>
   <motion.div initial={{opacity:0,y:18}} animate={{opacity:1,y:0}} className="auth-brandline"><span className="brandmark"><Sparkles size={17}/></span> SHOPSPHERE IDENTITY</motion.div>
   <motion.h1 initial={{opacity:0,y:25}} animate={{opacity:1,y:0}} transition={{delay:.08}}>Your shopping intelligence,<br/><span>in one place.</span></motion.h1>
   <motion.p initial={{opacity:0}} animate={{opacity:1}} transition={{delay:.18}}>Save wishlists and price alerts across sessions. Browse as a guest, then sign in when you want your account state synced.</motion.p>
   <div className="auth-points"><motion.span initial={{opacity:0,x:-15}} animate={{opacity:1,x:0}} transition={{delay:.28}}><ShieldCheck/> Secure token-based authentication</motion.span><motion.span initial={{opacity:0,x:-15}} animate={{opacity:1,x:0}} transition={{delay:.36}}><CheckCircle2/> Guest wishlist can be merged</motion.span><motion.span initial={{opacity:0,x:-15}} animate={{opacity:1,x:0}} transition={{delay:.44}}><LockKeyhole/> Passwords are hashed by the backend</motion.span></div>
  </div>
  <motion.form className="auth-card" initial={{opacity:0,x:40,scale:.97}} animate={{opacity:1,x:0,scale:1}} transition={{duration:.55}} onSubmit={submit}>
   <div className="auth-card-top"><div><div className="eyebrow">{mode==='login'?'WELCOME BACK':'NEW ACCOUNT'}</div><h2>{mode==='login'?'Sign in':'Create account'}</h2></div><motion.div className="auth-spark" animate={{rotate:[0,12,-8,0],scale:[1,1.08,1]}} transition={{duration:3,repeat:Infinity}}><Sparkles size={18}/></motion.div></div>
   <AnimatePresence mode="wait">
    <motion.div key={mode} initial={{opacity:0,y:8}} animate={{opacity:1,y:0}} exit={{opacity:0,y:-8}} transition={{duration:.2}}>
     {mode==='register'&&<label><span><UserRound size={15}/> Full name</span><input required minLength="2" value={name} onChange={e=>setName(e.target.value)} placeholder="Your name" autoComplete="name"/></label>}
     <label><span><Mail size={15}/> Email</span><input required value={email} onChange={e=>setEmail(e.target.value)} placeholder="you@example.com" type="email" autoComplete="email"/></label>
     <label><span><KeyRound size={15}/> Password</span><div className="password-wrap"><input required minLength="8" value={password} onChange={e=>setPassword(e.target.value)} placeholder="Minimum 8 characters" type={show?'text':'password'} autoComplete={mode==='login'?'current-password':'new-password'}/><button type="button" onClick={()=>setShow(!show)}>{show?<EyeOff size={16}/>:<Eye size={16}/>}</button></div></label>
     {mode==='register'&&<label><span><CheckCircle2 size={15}/> Confirm password</span><input required minLength="8" value={confirm} onChange={e=>setConfirm(e.target.value)} placeholder="Repeat your password" type={show?'text':'password'} autoComplete="new-password"/></label>}
     {mode==='register'&&password&&<div className={`password-match ${password===confirm?'ok':''}`}>{password===confirm&&confirm?<><CheckCircle2 size={14}/> Passwords match</>:<><LockKeyhole size={14}/> Make both passwords identical</>}</div>}
     <button className="primary auth-submit" disabled={busy} type="submit">{busy?<><span className="button-spinner"/> Working…</>:<>{mode==='login'?'Enter ShopSphere':'Create my account'} <ArrowRight size={16}/></>}</button>
     {error&&<motion.p initial={{opacity:0,y:4}} animate={{opacity:1,y:0}} className="error auth-error">{error}</motion.p>}
    </motion.div>
   </AnimatePresence>
   <div className="auth-divider"><span>OR</span></div>
   <button type="button" className="switch" onClick={switchMode}>{mode==='login'?'New here? Create an account':'Already registered? Sign in'}</button>
   <p className="auth-foot"><ShieldCheck size={13}/> Your account uses the same email and password you enter here.</p>
  </motion.form>
 </section>
}
