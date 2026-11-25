import { useRef, useState } from 'react'
import axios from 'axios'
import { X, Download, Play, Pause } from 'lucide-react'
import { getClipUrl } from './services/api'
import type { Clip } from './services/api'

export default function Editor({clip,onClose}:{clip:Clip;onClose:()=>void}) {
  const video=useRef<HTMLVideoElement>(null)
  const [captions,setCaptions]=useState(clip.captions ?? [])
  const [start,setStart]=useState(0)
  const [end,setEnd]=useState(clip.duration)
  const [time,setTime]=useState(0)
  const [playing,setPlaying]=useState(false)
  const [color,setColor]=useState('#ffffff')
  const [size,setSize]=useState(20)
  const [position,setPosition]=useState('bottom')
  const [bold,setBold]=useState(true)
  const [busy,setBusy]=useState(false)
  const [error,setError]=useState('')
  const [output,setOutput]=useState('')
  const active=captions.filter(c=>c.start<=time && time<c.end).map(c=>c.text).join(' ')
  function seek(t:number){if(video.current) video.current.currentTime=t;setTime(t)}
  async function render(){
    setBusy(true);setError('');setOutput('')
    try {const r=await axios.post<{download_url:string}>(getClipUrl(clip.editor_url!.replace(/\/source$/,'/render')),{start,end,captions,color,size,position,bold});setOutput(getClipUrl(r.data.download_url))}
    catch(e){setError(axios.isAxiosError(e)&&typeof e.response?.data?.detail==='string'?e.response.data.detail:'Export failed. Check the backend terminal.')}
    finally{setBusy(false)}
  }
  const field='w-full rounded border border-steel bg-carbon p-2 text-sm'
  return <div className="fixed inset-0 z-50 overflow-y-auto bg-obsidian text-offwhite">
    <header className="flex items-center justify-between border-b border-steel p-4"><div><h2 className="font-display text-xl">optivia. / Editor</h2><p className="text-xs text-muted">Vertical clip · 1080 × 1920</p></div><div className="flex items-center gap-4"><button disabled={busy||end-start<0.5} onClick={()=>void render()} className="rounded bg-silver px-4 py-2 text-obsidian disabled:opacity-50">{busy?'Rendering…':'Export video'}</button><button onClick={onClose} aria-label="Close editor"><X/></button></div></header>
    <div className="grid gap-5 p-5 lg:grid-cols-[1fr_1.4fr_1fr]">
      <section className="rounded-xl border border-steel bg-graphite p-4"><h3 className="mb-4 font-semibold">Transcript</h3><div className="max-h-[65vh] space-y-3 overflow-y-auto">{captions.map((c,i)=><div key={i}><button onClick={()=>seek(c.start)} className="mb-1 text-xs text-nardo">{c.start.toFixed(2)} – {c.end.toFixed(2)}s</button><textarea className={field} value={c.text} maxLength={1000} onChange={e=>setCaptions(old=>old.map((x,j)=>j===i?{...x,text:e.target.value}:x))}/></div>)}</div></section>
      <section className="flex flex-col items-center gap-3"><div className="relative aspect-[9/16] w-full max-w-[300px] overflow-hidden rounded-xl bg-black"><video ref={video} src={getClipUrl(clip.editor_url!)} playsInline className="h-full w-full object-contain" onPlay={()=>setPlaying(true)} onPause={()=>setPlaying(false)} onTimeUpdate={()=>{const v=video.current;if(!v)return;setTime(v.currentTime);if(v.currentTime>=end){v.pause();v.currentTime=end}}}/><div className="pointer-events-none absolute inset-x-3 text-center" style={{color,fontSize:size*0.85,fontWeight:bold?700:400,textShadow:'1px 1px 3px black, -1px -1px 2px black',top:position==='top'?'12%':position==='middle'?'50%':undefined,bottom:position==='bottom'?'12%':undefined}}>{active}</div></div><button aria-label={playing?'Pause':'Play'} onClick={()=>{const v=video.current;if(!v)return;if(playing)v.pause();else{if(v.currentTime<start||v.currentTime>=end)seek(start);void v.play().catch(()=>setError('Unable to play source'))}}}>{playing?<Pause/>:<Play/>}</button><span className="text-sm text-nardo">{time.toFixed(2)} / {clip.duration.toFixed(2)}s</span></section>
      <section className="space-y-4 rounded-xl border border-steel bg-graphite p-4"><h3 className="font-semibold">Caption style</h3><div className="flex flex-wrap gap-2">{['Minimal','Bold','Cinematic'].map(p=><button key={p} className="rounded border border-steel px-3 py-2 text-xs" onClick={()=>{setBold(p!=='Minimal');setSize(p==='Bold'?28:18);setColor(p==='Cinematic'?'#ffdd88':'#ffffff');setPosition('bottom')}}>{p}</button>)}</div><label className="block">Color <input type="color" value={color} onChange={e=>setColor(e.target.value)}/></label><label className="block">Size: {size}<input className="w-full" type="range" min={12} max={32} value={size} onChange={e=>setSize(+e.target.value)}/></label><label className="block">Position<select className={field} value={position} onChange={e=>setPosition(e.target.value)}><option>bottom</option><option>middle</option><option>top</option></select></label><label><input type="checkbox" checked={bold} onChange={e=>setBold(e.target.checked)}/> Bold</label>{error&&<p className="text-red-400">{error}</p>}{output&&<a className="flex gap-2 text-green-400" href={output}><Download size={18}/> Download rendered video</a>}</section>
    </div><section className="mx-5 mb-5 space-y-3 rounded-xl border border-steel bg-graphite p-4"><h3 className="font-semibold">Timeline</h3><input aria-label="Playhead" type="range" className="w-full" min={0} max={clip.duration} step={0.01} value={time} onChange={e=>seek(+e.target.value)}/><div className="relative h-8 rounded bg-carbon"><div className="absolute h-full rounded bg-silver/30" style={{left:`${start/clip.duration*100}%`,width:`${(end-start)/clip.duration*100}%`}}/></div><div className="relative h-6 rounded bg-carbon">{captions.map((c,i)=><div key={i} title={c.text} className="absolute h-full overflow-hidden rounded border border-graphite bg-steel text-[10px]" style={{left:`${c.start/clip.duration*100}%`,width:`${(c.end-c.start)/clip.duration*100}%`}}>{c.text}</div>)}</div><div className="grid grid-cols-2 gap-4"><label>In: {start.toFixed(2)}s<input type="range" className="w-full" min={0} max={Math.max(0,end-0.5)} step={0.01} value={start} onChange={e=>{setStart(+e.target.value);seek(+e.target.value)}}/></label><label>Out: {end.toFixed(2)}s<input type="range" className="w-full" min={start+0.5} max={clip.duration} step={0.01} value={end} onChange={e=>setEnd(+e.target.value)}/></label></div></section>
  </div>
}
