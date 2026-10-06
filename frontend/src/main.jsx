import React,{useEffect,useMemo,useState} from 'react'
import {createRoot} from 'react-dom/client'
import {BrowserRouter,useNavigate,useParams,useLocation,Routes,Route,Link} from 'react-router-dom'
import {api,wsBase} from './lib/api'
import {Rocket,LogOut,Plus,User,ArrowRight,CheckCircle2,Clock3,AlertTriangle,Download,BarChart3,ShieldCheck,Sparkles} from 'lucide-react'
import {LineChart,Line,XAxis,YAxis,Tooltip,ResponsiveContainer,CartesianGrid} from 'recharts'
import './index.css'

function Layout({children}){
  const nav=useNavigate();
  const [me,setMe]=useState(null);

  useEffect(()=>{
    api.get('/api/auth/me').then(r=>setMe(r.data)).catch(()=>{});
  },[]);

  return (
    <div className="min-h-screen bg-[#f6f3ed] text-[#181715]">
      <header className="site-header sticky top-0 z-30">
        <div className="site-nav max-w-7xl mx-auto px-5 h-[72px] flex items-center justify-between">

          <Link to="/" className="brand flex items-center gap-3">
            <span className="brand-mark">
              <Rocket size={17}/>
            </span>
            <span className="text-[19px] font-black tracking-[-0.03em]">
              StartupPilot
              <span className="brand-accent"> AI</span>
            </span>
          </Link>

          <nav className="hidden md:flex items-center gap-1 nav-links">
            <Link to="/dashboard" className="nav-link">Dashboard</Link>
            <Link to="/new" className="nav-link nav-new">
              <Plus size={15}/>
              New Analysis
            </Link>
            <Link to="/history" className="nav-link">History</Link>
            <Link to="/profile" className="nav-link">Profile</Link>
          </nav>

          <div className="flex items-center">
            {me ? (
              <button
                onClick={()=>{localStorage.removeItem('sp_token');nav('/login')}}
                className="logout-button"
              >
                <span className="logout-name">{me.name?.split(' ')[0] || 'Account'}</span>
                <LogOut size={15}/>
              </button>
            ) : (
              <Link to="/login" className="login-button">Login</Link>
            )}
          </div>

        </div>
      </header>

      <main>{children}</main>
    </div>
  );
}
function Landing(){
  const [selectedAgent,setSelectedAgent]=useState(null);

  const agents={
    Marketing:{
      number:'01',
      title:'Marketing',
      short:'Market research, audience & go-to-market',
      kicker:'MARKETING INTELLIGENCE',
      description:'The Marketing Agent studies the market around your startup idea and builds a practical customer acquisition strategy.',
      points:[
        'Market overview and competitive landscape',
        'Target audience and ideal customer profile',
        'Customer pain points and market opportunities',
        'Go-to-market strategy and acquisition channels',
        'Marketing budget allocation, ad copies and SEO keywords'
      ]
    },
    Finance:{
      number:'02',
      title:'Finance',
      short:'Revenue model, costs & projections',
      kicker:'FINANCIAL INTELLIGENCE',
      description:'The Finance Agent converts the marketing strategy into a financially coherent startup model using explicit assumptions and calculations.',
      points:[
        'Recommended revenue model',
        'Revenue and cost assumptions',
        'Year-1 financial projections',
        'Break-even analysis',
        'Unit economics and financial risks'
      ]
    },
    Product:{
      number:'03',
      title:'Product',
      short:'MVP scope, user stories & roadmap',
      kicker:'PRODUCT INTELLIGENCE',
      description:'The Product Agent turns customer needs and financial constraints into a focused MVP and actionable product roadmap.',
      points:[
        'Product vision and MVP scope',
        'Core features and requirements',
        'At least five user stories',
        'MoSCoW feature priorities',
        'Product roadmap and implementation direction'
      ]
    },
    Validator:{
      number:'04',
      title:'Validator',
      short:'Consistency checks & final business review',
      kicker:'VALIDATION INTELLIGENCE',
      description:'The Validator Agent independently reviews the Marketing, Finance and Product outputs to identify contradictions, unsupported claims and risky assumptions.',
      points:[
        'Overall consistency score',
        'Cross-agent contradiction checks',
        'Unsupported claim detection',
        'Assumption and risk review',
        'Final validation status and recommendations'
      ]
    }
  };

  const selectAgent=(name)=>{
    setSelectedAgent(name);
    setTimeout(()=>{
      document.getElementById('agent-specifications')?.scrollIntoView({
        behavior:'smooth',
        block:'start'
      });
    },50);
  };

  const selected=selectedAgent ? agents[selectedAgent] : null;

  return (
    <div className="landing-page">

      <section className="landing-hero">
        <div className="hero-grid max-w-7xl mx-auto px-5">

          <div className="hero-copy">
            <div className="eyebrow">
              <span className="eyebrow-dot"></span>
              STARTUP INTELLIGENCE PLATFORM
            </div>

            <h1>
              Turn your idea into
              <span className="hero-highlight"> a real business plan.</span>
            </h1>

            <p className="hero-description">
              Research-backed startup analysis powered by specialized AI agents
              working together across marketing, finance and product strategy.
            </p>

            <div className="hero-actions">
              <Link to="/new" className="primary-cta">
                Create Business Plan
                <ArrowRight size={17}/>
              </Link>

              <Link to="/dashboard" className="secondary-cta">
                Explore workspace
              </Link>
            </div>

            <div className="hero-meta">
              <span><CheckCircle2 size={15}/> Research-backed</span>
              <span><CheckCircle2 size={15}/> Multi-agent workflow</span>
              <span><CheckCircle2 size={15}/> PDF reports</span>
            </div>
          </div>

          <div className="agent-panel">

            <div className="agent-panel-header">
              <div>
                <div className="panel-kicker">THE WORKFLOW</div>
                <div className="panel-title">From idea to strategy</div>
              </div>

              <div className="live-indicator">
                <span></span>
                LIVE
              </div>
            </div>

            <div className="agent-list">

              {Object.entries(agents).map(([name,agent],index)=>(
                <div key={name}>
                  <button
                    type="button"
                    className={`agent-item ${selectedAgent===name?'agent-item-selected':''}`}
                    onClick={()=>selectAgent(name)}
                    aria-label={`View ${name} agent specification`}
                  >
                    <div className="agent-number">{agent.number}</div>

                    <div className="agent-info">
                      <div className="agent-name">{agent.title}</div>
                      <div className="agent-desc">{agent.short}</div>
                    </div>

                    {name==='Validator'
                      ? <CheckCircle2 size={18} className="validator-icon"/>
                      : <ArrowRight size={17} className="agent-arrow"/>
                    }
                  </button>

                  {index<Object.keys(agents).length-1 &&
                    <div className="workflow-line"></div>
                  }
                </div>
              ))}

            </div>

            <div className="agent-panel-hint">
              Click an agent to explore its responsibilities
            </div>

          </div>

        </div>
      </section>

      <section
        id="agent-specifications"
        className="agent-specifications"
      >
        <div className="max-w-7xl mx-auto px-5">

          <div className="feature-intro">
            <div>
              <div className="section-kicker">AGENT SPECIFICATIONS</div>
              <h2>
                {selected
                  ? `${selected.title} Agent`
                  : 'How the AI team works'}
              </h2>
            </div>

            <p>
              {selected
                ? selected.description
                : 'Select an agent above to understand exactly what it contributes to your startup analysis.'}
            </p>
          </div>

          {selected ? (
            <div className="selected-agent-spec">

              <div className="selected-agent-header">
                <div className="selected-agent-number">
                  {selected.number}
                </div>

                <div>
                  <div className="section-kicker">{selected.kicker}</div>
                  <h3>{selected.title}</h3>
                </div>
              </div>

              <div className="spec-grid">
                {selected.points.map((point,index)=>(
                  <div className="spec-item" key={point}>
                    <span>{String(index+1).padStart(2,'0')}</span>
                    <p>{point}</p>
                  </div>
                ))}
              </div>

              <button
                type="button"
                className="spec-back"
                onClick={()=>setSelectedAgent(null)}
              >
                View all agent responsibilities
              </button>

            </div>
          ) : (
            <div className="feature-grid">

              <button
                type="button"
                className="feature-card"
                onClick={()=>selectAgent('Marketing')}
              >
                <div className="feature-number">01</div>
                <h3>Marketing Agent</h3>
                <p>
                  Researches customers, competitors, opportunities and
                  go-to-market strategy.
                </p>
              </button>

              <button
                type="button"
                className="feature-card"
                onClick={()=>selectAgent('Finance')}
              >
                <div className="feature-number">02</div>
                <h3>Finance Agent</h3>
                <p>
                  Builds the revenue model, financial assumptions,
                  projections and break-even analysis.
                </p>
              </button>

              <button
                type="button"
                className="feature-card"
                onClick={()=>selectAgent('Product')}
              >
                <div className="feature-number">03</div>
                <h3>Product Agent</h3>
                <p>
                  Defines the MVP, user stories, priorities and
                  product roadmap.
                </p>
              </button>

              <button
                type="button"
                className="feature-card"
                onClick={()=>selectAgent('Validator')}
              >
                <div className="feature-number">04</div>
                <h3>Validator Agent</h3>
                <p>
                  Checks consistency, unsupported claims, assumptions
                  and contradictions across the analysis.
                </p>
              </button>

              <div className="feature-card">
                <div className="feature-number">05</div>
                <h3>Sequential workflow</h3>
                <p>
                  Marketing → Finance → Product → Validator,
                  with each stage receiving the required previous context.
                </p>
              </div>

            </div>
          )}

        </div>
      </section>

    </div>
  );
}

function Dashboard(){const [runs,setRuns]=useState([]);useEffect(()=>{api.get('/api/runs').then(r=>setRuns(r.data)).catch(()=>{})},[]);return <div className="max-w-7xl mx-auto px-5 py-10"><div className="flex justify-between items-end mb-8"><div><p className="text-violet-600 font-semibold">Workspace</p><h1 className="text-3xl font-black">Dashboard</h1></div><Link to="/new" className="gradient text-white px-4 py-2.5 rounded-xl flex gap-2 items-center"><Plus size={18}/>New Analysis</Link></div><div className="grid md:grid-cols-3 gap-5 mb-8">{[['Analyses',runs.length],['Completed',runs.filter(x=>x.status==='completed').length],['In progress',runs.filter(x=>!['completed','failed'].includes(x.status)).length]].map(([a,b])=><div className="card p-5" key={a}><div className="text-slate-500 text-sm">{a}</div><div className="text-3xl font-black mt-2">{b}</div></div>)}</div><div className="card p-6"><h2 className="font-bold text-lg mb-4">Recent analyses</h2>{runs.slice(0,6).map(r=><Link to={`/analysis/${r.run_id}`} className="flex items-center justify-between py-4 border-b last:border-0" key={r.run_id}><div><div className="font-semibold line-clamp-1">{r.startup_idea}</div><div className="text-xs text-slate-500 mt-1">{new Date(r.created_at).toLocaleString()}</div></div><Status status={r.status}/></Link>)}{!runs.length&&<div className="text-slate-500 py-8 text-center">No analyses yet. Create your first business plan.</div>}</div></div>}
function Status({status}){const done=status==='completed';const fail=status==='failed';return <span className={`text-xs px-2.5 py-1 rounded-full ${done?'bg-emerald-50 text-emerald-700':fail?'bg-red-50 text-red-700':'bg-amber-50 text-amber-700'}`}>{status.replaceAll('_',' ')}</span>}
function NewAnalysis(){const nav=useNavigate();const [idea,setIdea]=useState('AI-powered platform that helps college students find affordable healthy meals near their campus.');const [err,setErr]=useState('');async function submit(){try{const r=await api.post('/api/run',{startup_idea:idea});nav(`/analysis/${r.data.run_id}`)}catch(e){setErr(e.response?.data?.detail||'Could not start analysis')}}return <div className="max-w-4xl mx-auto px-5 py-12"><p className="text-violet-600 font-semibold">New analysis</p><h1 className="text-4xl font-black mt-1">Describe your startup idea</h1><p className="text-slate-500 mt-2">The core workflow works with only the startup idea.</p><textarea className="w-full min-h-72 border rounded-2xl p-5 mt-8 focus:outline-none focus:ring-2 focus:ring-violet-200" value={idea} onChange={e=>setIdea(e.target.value)} placeholder="Example: I want to build..."/><div className="bg-amber-50 border border-amber-100 rounded-xl p-4 text-sm mt-4 text-amber-800">AI-generated business analysis may contain estimates and should be verified before making real financial or business decisions.</div>{err&&<div className="text-red-600 mt-3">{err}</div>}<button onClick={submit} disabled={idea.trim().length<20} className="gradient text-white px-6 py-3 rounded-xl font-semibold mt-5 disabled:opacity-50">Generate Business Plan</button></div>}
function Analysis(){const {id}=useParams();const nav=useNavigate();const [run,setRun]=useState(null);const [report,setReport]=useState(null);const [events,setEvents]=useState([]);useEffect(()=>{let timer=setInterval(()=>api.get(`/api/run/${id}`).then(r=>setRun(r.data)).catch(()=>{}),1500);api.get(`/api/report/${id}`).then(r=>setReport(r.data)).catch(()=>{});const token=localStorage.getItem('sp_token');let ws;try{ws=new WebSocket(`${wsBase}/ws/${id}?token=${encodeURIComponent(token||'')}`);ws.onmessage=e=>{const d=JSON.parse(e.data);setEvents(v=>[...v,d]);if(d.status==='completed')api.get(`/api/report/${id}`).then(r=>setReport(r.data))}}catch{}return()=>{clearInterval(timer);ws?.close()}},[id]);if(!report)return <Progress run={run} events={events}/>;return <Report report={report} nav={nav}/>}
function Progress({run,events}){const statuses=['marketing','finance','product','validation'];const current=run?.status||'queued';return <div className="max-w-5xl mx-auto px-5 py-12"><div className="text-center mb-10"><div className="w-16 h-16 rounded-2xl gradient text-white grid place-items-center mx-auto"><Sparkles/></div><h1 className="text-3xl font-black mt-4">Building your business plan</h1><p className="text-slate-500 mt-2">Specialized agents are collaborating in sequence.</p></div><div className="grid md:grid-cols-4 gap-4">{statuses.map((s,i)=>{const running=current===`${s}_running`,done=current===`${s}_completed`||['product_completed','validation_running','completed'].includes(current)&&i<4;return <div className="card p-5" key={s}><div className="flex justify-between"><span className="font-bold capitalize">{s} Agent</span>{done?<CheckCircle2 className="text-emerald-500"/>:running?<Clock3 className="text-amber-500"/>:<Clock3 className="text-slate-300"/>}</div><div className="text-sm text-slate-500 mt-2">{done?'Completed':running?'Running':'Waiting'}</div></div>})}</div><div className="card p-5 mt-6"><h3 className="font-bold mb-3">Live activity</h3>{events.slice(-8).map((e,i)=><div className="text-sm py-2" key={i}>{e.message||e.type}</div>)}{!events.length&&<div className="text-sm text-slate-500">Startup analysis started...</div>}</div><div className="text-xs text-slate-400 mt-5">Status is also persisted in the backend, so refresh/reconnect is safe.</div></div>}
function Report({report,nav}){const [tab,setTab]=useState('overview');const tabs=['overview','marketing','finance','product','validation','sources'];const f=report.finance;return <div className="max-w-7xl mx-auto px-5 py-10"><div className="flex flex-col md:flex-row md:items-end justify-between gap-4 mb-6"><div><p className="text-violet-600 font-semibold">Business plan</p><h1 className="text-3xl font-black">{report.startup_idea}</h1></div><button onClick={async()=>{const r=await api.get(`/api/report/${report.run_id}/pdf`,{responseType:'blob'});const u=URL.createObjectURL(r.data);const a=document.createElement('a');a.href=u;a.download=`startuppilot-${report.run_id}.pdf`;a.click();URL.revokeObjectURL(u)}} className="bg-[#c65d35] hover:bg-[#ad4f2d] text-white px-5 py-2.5 rounded-xl flex gap-2 items-center font-semibold shadow-sm transition-colors"><Download size={17}/>Export PDF</button></div><div className="flex gap-2 overflow-x-auto pb-3">{tabs.map(x=><button key={x} onClick={()=>setTab(x)} className={`px-4 py-2 rounded-xl capitalize ${tab===x?'gradient text-white':'bg-white border'}`}>{x}</button>)}</div>{tab==='overview'&&<div className="grid md:grid-cols-4 gap-4">{[['Validation',report.validation.overall_consistency_score+'/100'],['Break-even',f.break_even.break_even_month?`Month ${f.break_even.break_even_month}`:'Not reached'],['Revenue model',f.recommended_revenue_model],['Mode',report.execution_mode==='fallback_demo'?'Fallback Mode':(report.demo_mode?'Demo Mode':'Live AI')]].map(([a,b])=><div className="card p-5" key={a}><div className="text-sm text-slate-500">{a}</div><div className="font-bold mt-2">{b}</div></div>)}<div className="card p-5 md:col-span-4"><h2 className="font-bold text-lg mb-2">Executive view</h2><p className="text-slate-600">{f.executive_summary}</p></div></div>}{tab==='marketing'&&<Section data={report.marketing}/>} {tab==='finance'&&<Finance data={f}/>} {tab==='product'&&<Section data={report.product}/>} {tab==='validation'&&<Validation data={report.validation}/>} {tab==='sources'&&<Sources data={report.sources}/>}<div className="mt-8 text-sm text-slate-500">{report.execution_mode==='fallback_demo' && <span className="block text-amber-700 font-semibold mb-2">Fallback Mode — simulated AI responses were used because the live Gemini service was temporarily unavailable.</span>}AI-generated outputs contain assumptions and estimates. Verify before real decisions.</div></div>}
function Section({data}){return <div className="grid md:grid-cols-2 gap-5">{Object.entries(data).filter(([k])=>!['sources'].includes(k)).map(([k,v])=><div className="card p-5" key={k}><h3 className="font-bold capitalize">{k.replaceAll('_',' ')}</h3><pre className="whitespace-pre-wrap text-sm text-slate-600 mt-3 font-sans">{typeof v==='string'?v:JSON.stringify(v,null,2)}</pre></div>)}</div>}
function Finance({data}){return <div className="space-y-5"><div className="card p-5"><h2 className="font-bold mb-4">Year-1 revenue & profit/loss</h2><div className="h-80"><ResponsiveContainer><LineChart data={data.year1_projection}><CartesianGrid strokeDasharray="3 3"/><XAxis dataKey="month"/><YAxis/><Tooltip/><Line type="monotone" dataKey="revenue" stroke="#6d5dfc"/><Line type="monotone" dataKey="profit_loss" stroke="#111827"/></LineChart></ResponsiveContainer></div></div><Section data={data}/></div>}
function Validation({data}){return <div className="grid md:grid-cols-2 gap-5"><div className="card p-6 md:col-span-2"><div className="flex items-center gap-3"><ShieldCheck className="text-emerald-500"/><span className="text-3xl font-black">{data.overall_consistency_score}/100</span><Status status={data.final_validation_status.toLowerCase().replaceAll(' ','_')}/></div></div><Section data={data}/></div>}
function Sources({data}){return <div className="card p-6">{data.map((s,i)=><div key={i} className="py-4 border-b last:border-0"><div className="font-semibold">{s.title||'Source'}</div><a className="text-violet-600 text-sm break-all" href={s.url} target="_blank">{s.url}</a></div>)}{!data.length&&<div className="text-slate-500">No live research sources were available for this run.</div>}</div>}
function History(){const [runs,setRuns]=useState([]);useEffect(()=>{api.get('/api/runs').then(r=>setRuns(r.data))},[]);return <div className="max-w-7xl mx-auto px-5 py-10"><h1 className="text-3xl font-black">Analysis History</h1><div className="card p-5 mt-6">{runs.map(r=><Link className="flex justify-between py-4 border-b last:border-0" to={`/analysis/${r.run_id}`} key={r.run_id}><span className="line-clamp-1 mr-4">{r.startup_idea}</span><Status status={r.status}/></Link>)}</div></div>}
function Profile(){
  const [me,setMe]=useState(null);
  const [error,setError]=useState('');

  useEffect(()=>{
    api.get('/api/auth/me')
      .then(r=>setMe(r.data))
      .catch(()=>setError('Unable to load profile information.'));
  },[]);

  return <div className="max-w-3xl mx-auto px-5 py-10">
    <div className="card p-7">
      <div className="flex items-center gap-3">
        <div className="w-12 h-12 rounded-full bg-violet-100 grid place-items-center">
          <User className="text-violet-600"/>
        </div>
        <div>
          <h1 className="text-2xl font-black">Profile</h1>
          <p className="text-sm text-slate-500">Your StartupPilot AI account</p>
        </div>
      </div>

      {error && <div className="mt-6 p-4 rounded-xl bg-red-50 text-red-600 text-sm">{error}</div>}

      {!me && !error && <div className="mt-6 text-slate-500">Loading profile...</div>}

      {me && <div className="mt-7 space-y-4">
        <div className="p-4 rounded-xl bg-slate-50">
          <div className="text-xs font-semibold text-slate-500 uppercase tracking-wide">Name</div>
          <div className="font-semibold mt-1">{me.name}</div>
        </div>

        <div className="p-4 rounded-xl bg-slate-50">
          <div className="text-xs font-semibold text-slate-500 uppercase tracking-wide">Email</div>
          <div className="font-semibold mt-1">{me.email}</div>
        </div>

        <div className="p-4 rounded-xl bg-slate-50">
          <div className="text-xs font-semibold text-slate-500 uppercase tracking-wide">Account ID</div>
          <div className="font-mono text-sm mt-1 break-all">{me.id}</div>
        </div>

        <div className="p-4 rounded-xl bg-emerald-50">
          <div className="text-xs font-semibold text-emerald-700 uppercase tracking-wide">Security</div>
          <div className="text-sm text-emerald-800 mt-1">
            JWT authentication enabled · Password protected with bcrypt hashing
          </div>
        </div>
      </div>}
    </div>
  </div>
}

function Auth({register=false}){
  const nav=useNavigate();
  const [name,setName]=useState('');
  const [email,setEmail]=useState('');
  const [password,setPassword]=useState('');
  const [error,setError]=useState('');
  const [loading,setLoading]=useState(false);

  async function submit(e){
    e.preventDefault();
    setError('');
    setLoading(true);

    try{
      const endpoint=register ? '/api/auth/register' : '/api/auth/login';
      const payload=register
        ? {name,email,password}
        : {email,password};

      const r=await api.post(endpoint,payload);

      localStorage.setItem('sp_token',r.data.access_token);
      nav('/dashboard');
    }catch(e){
      setError(
        e.response?.data?.detail ||
        (register ? 'Could not create account.' : 'Invalid email or password.')
      );
    }finally{
      setLoading(false);
    }
  }

  return (
    <div className="max-w-md mx-auto px-5 py-14">
      <div className="card p-7">
        <div className="text-center mb-7">
          <div className="w-12 h-12 rounded-xl gradient text-white grid place-items-center mx-auto mb-4">
            <Rocket size={22}/>
          </div>
          <h1 className="text-2xl font-black">
            {register ? 'Create your account' : 'Welcome back'}
          </h1>
          <p className="text-sm text-slate-500 mt-2">
            {register
              ? 'Start building smarter startup strategies.'
              : 'Sign in to continue to StartupPilot AI.'}
          </p>
        </div>

        {error && (
          <div className="mb-5 p-3 rounded-xl bg-red-50 border border-red-100 text-red-600 text-sm">
            {error}
          </div>
        )}

        <form onSubmit={submit} className="space-y-4">
          {register && (
            <div>
              <label className="text-sm font-semibold">Name</label>
              <input
                className="w-full border rounded-xl px-4 py-3 mt-1.5"
                value={name}
                onChange={e=>setName(e.target.value)}
                placeholder="Your name"
                required
              />
            </div>
          )}

          <div>
            <label className="text-sm font-semibold">Email</label>
            <input
              type="email"
              className="w-full border rounded-xl px-4 py-3 mt-1.5"
              value={email}
              onChange={e=>setEmail(e.target.value)}
              placeholder="you@example.com"
              required
            />
          </div>

          <div>
            <label className="text-sm font-semibold">Password</label>
            <input
              type="password"
              className="w-full border rounded-xl px-4 py-3 mt-1.5"
              value={password}
              onChange={e=>setPassword(e.target.value)}
              placeholder="Enter your password"
              minLength={6}
              required
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="gradient text-white w-full py-3 rounded-xl font-semibold disabled:opacity-50"
          >
            {loading
              ? (register ? 'Creating account...' : 'Signing in...')
              : (register ? 'Create Account' : 'Sign In')}
          </button>
        </form>

        <div className="text-center text-sm text-slate-500 mt-6">
          {register ? 'Already have an account?' : "Don't have an account?"}{' '}
          <button
            type="button"
            onClick={()=>nav(register ? '/login' : '/register')}
            className="text-violet-600 font-semibold"
          >
            {register ? 'Sign in' : 'Create one'}
          </button>
        </div>
      </div>
    </div>
  );
}

function App(){return <Layout><Routes><Route path="/" element={<Landing/>}/><Route path="/login" element={<Auth/>}/><Route path="/register" element={<Auth register/>}/><Route path="/dashboard" element={<Dashboard/>}/><Route path="/new" element={<NewAnalysis/>}/><Route path="/analysis/:id" element={<Analysis/>}/><Route path="/history" element={<History/>}/><Route path="/profile" element={<Profile/>}/></Routes></Layout>}
createRoot(document.getElementById('root')).render(<BrowserRouter><App/></BrowserRouter>)
