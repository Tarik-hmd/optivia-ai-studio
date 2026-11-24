
import { useEffect, useRef, useState } from 'react'
import {
  LayoutDashboard,
  FolderOpen,
  Film,
  Plus,
  UploadCloud,
  ScanLine,
  ArrowUpRight,
  Download,
  Clock,
  LoaderCircle,
  CheckCircle2,
  AlertCircle,
  Sparkles,
  X,
  Menu,
  Cpu,
} from 'lucide-react'
import { motion } from 'motion/react'
import axios from 'axios'

import {
  checkHealth,
  processVideo,
  getClipUrl,
} from './services/api'

import type {
  Clip,
  ProcessingMode,
  ProcessingResult,
} from './services/api'

type Page = 'Overview' | 'Projects' | 'My clips'

interface Project {
  name: string
  result: ProcessingResult
}

function App() {
  const [page, setPage] = useState<Page>('Overview')
  const [online, setOnline] = useState(false)
  const [file, setFile] = useState<File | null>(null)
  const [mode, setMode] =
    useState<ProcessingMode>('keywords')
  const [processing, setProcessing] = useState(false)
  const [error, setError] = useState('')
  const [dragging, setDragging] = useState(false)
  const [mobileMenu, setMobileMenu] = useState(false)
  const [projects, setProjects] = useState<Project[]>([])
  const [selectedClip, setSelectedClip] =
    useState<Clip | null>(null)

  const inputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    const refresh = async () => {
      setOnline(await checkHealth())
    }

    void refresh()
    const interval = setInterval(refresh, 10000)

    return () => clearInterval(interval)
  }, [])

  const allClips = projects.flatMap(
    project => project.result.clips
  )

  const totalDuration = allClips.reduce(
    (sum, clip) => sum + clip.duration,
    0
  )

  function selectFile(newFile: File) {
    setError('')

    if (!newFile.name.toLowerCase().endsWith('.mp4')) {
      setError('Please select an MP4 video.')
      return
    }

    if (newFile.size > 500 * 1024 * 1024) {
      setError('Your video exceeds the 500 MB limit.')
      return
    }

    setFile(newFile)
  }

  async function generate() {
    if (!file || processing) return

    setProcessing(true)
    setError('')

    try {
      const result = await processVideo(file, mode)

      setProjects(previous => [
        { name: file.name, result },
        ...previous,
      ])

      setFile(null)
      setPage('My clips')
    } catch (err) {
      if (axios.isAxiosError(err)) {
        const detail = err.response?.data?.detail

        setError(
          typeof detail === 'string'
            ? detail
            : 'Unable to process your video.'
        )
      } else {
        setError('An unexpected error occurred.')
      }
    } finally {
      setProcessing(false)
    }
  }

  const navigation = [
    { name: 'Overview' as const, icon: LayoutDashboard },
    { name: 'Projects' as const, icon: FolderOpen },
    { name: 'My clips' as const, icon: Film },
  ]

  return (
    <div className="min-h-screen bg-obsidian text-offwhite">

      {/* Sidebar */}
      <aside className={`
        fixed inset-y-0 left-0 z-40 w-64
        flex-col border-r border-steel bg-graphite p-5
        ${mobileMenu ? 'flex' : 'hidden'} md:flex
      `}>
        <div className="mb-12 flex items-center gap-3">
          <div className="rounded-lg bg-silver p-2 text-obsidian">
            <ScanLine size={23} />
          </div>

          <div>
            <h1 className="font-display text-2xl font-bold tracking-tight">
              optivia.
            </h1>
            <p className="text-[10px] tracking-[0.3em] text-nardo">
              AI STUDIO
            </p>
          </div>
        </div>

        <button
          onClick={() => {
            setPage('Overview')
            setMobileMenu(false)
          }}
          className="mb-10 flex items-center justify-center
          gap-2 rounded-lg bg-silver px-4 py-3
          text-sm font-semibold text-obsidian hover:bg-offwhite"
        >
          <Plus size={18} />
          New project
        </button>

        <p className="mb-4 text-[10px] font-semibold
          tracking-[0.2em] text-muted">
          WORKSPACE
        </p>

        <nav className="space-y-2">
          {navigation.map(item => (
            <button
              key={item.name}
              onClick={() => {
                setPage(item.name)
                setMobileMenu(false)
              }}
              className={`flex w-full items-center gap-3
                rounded-lg px-3 py-3 text-sm
                ${page === item.name
                  ? 'bg-steel text-offwhite'
                  : 'text-muted hover:bg-carbon hover:text-offwhite'
                }`}
            >
              <item.icon size={18} />
              {item.name}
            </button>
          ))}
        </nav>

        <div className="mt-auto border-t border-steel pt-5">
          <div className="flex items-center gap-2 text-xs">
            <span className={`h-2 w-2 rounded-full ${
              online ? 'bg-emerald-400' : 'bg-red-400'
            }`} />
            {online ? 'Engine online' : 'Engine offline'}
          </div>
          <p className="mt-3 text-[10px] tracking-widest text-muted">
            OPTIVIA / VERSION 1.0
          </p>
        </div>
      </aside>

      {/* Main workspace */}
      <main className="min-h-screen md:ml-64">

        <header className="flex h-18 items-center
          justify-between border-b border-steel px-6 lg:px-10">

          <div className="flex items-center gap-3">
            <button
              className="md:hidden"
              onClick={() => setMobileMenu(!mobileMenu)}
              aria-label="Toggle menu"
            >
              <Menu size={22} />
            </button>

            <span className="text-xs tracking-widest text-muted">
              WORKSPACE / {page.toUpperCase()}
            </span>
          </div>

          <span className="rounded-full border border-steel
            px-3 py-1 text-xs text-nardo">
            STUDIO V1
          </span>
        </header>

        <div className="mx-auto max-w-7xl p-6 lg:p-10">

          {error && (
            <div className="mb-6 flex items-center gap-3
              rounded-lg border border-red-900 bg-red-950/30
              p-4 text-sm text-red-300">
              <AlertCircle size={18} />
              <span className="flex-1">{error}</span>
              <button onClick={() => setError('')}>
                <X size={16} />
              </button>
            </div>
          )}

          {processing && (
            <div className="mb-6 flex items-center gap-4
              rounded-xl border border-steel bg-carbon p-5">
              <LoaderCircle className="animate-spin text-nardo" />
              <div>
                <p className="font-medium">Processing your video</p>
                <p className="mt-1 text-xs text-muted">
                  Transcribing, ranking and exporting clips.
                  This may take several minutes.
                </p>
              </div>
            </div>
          )}

          {page === 'Overview' && (
            <motion.div
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
            >
              <p className="mb-4 text-xs tracking-[0.25em] text-nardo">
                INTELLIGENT CONTENT CREATION
              </p>

              <h2 className="font-display text-4xl
                font-semibold tracking-tight lg:text-6xl">
                Create more.
                <span className="block text-nardo">Edit less.</span>
              </h2>

              <p className="mb-10 mt-4 text-sm text-muted">
                Transform long-form content into powerful short videos.
              </p>

              {/* Upload area */}
              <div
                onDragOver={event => {
                  event.preventDefault()
                  setDragging(true)
                }}
                onDragLeave={() => setDragging(false)}
                onDrop={event => {
                  event.preventDefault()
                  setDragging(false)
                  const dropped = event.dataTransfer.files[0]
                  if (dropped && !processing) selectFile(dropped)
                }}
                className={`rounded-xl border border-dashed
                  bg-graphite p-10 text-center transition-colors
                  ${dragging ? 'border-silver' : 'border-nardo/40'}`}
              >
                <input
                  ref={inputRef}
                  type="file"
                  accept=".mp4,video/mp4"
                  className="hidden"
                  onChange={event => {
                    const selected = event.target.files?.[0]
                    if (selected) selectFile(selected)
                    event.target.value = ''
                  }}
                />

                <div className="mx-auto mb-5 flex h-16 w-16
                  items-center justify-center rounded-2xl
                  border border-steel bg-carbon">
                  {file
                    ? <CheckCircle2 size={28} className="text-silver" />
                    : <UploadCloud size={28} className="text-nardo" />
                  }
                </div>

                <h3 className="font-display text-xl font-semibold">
                  {file ? file.name : 'Import your footage'}
                </h3>

                <p className="mb-6 mt-2 text-xs text-muted">
                  {file
                    ? `${(file.size / 1024 / 1024).toFixed(1)} MB`
                    : 'Drag and drop your video · MP4 · Max 500 MB'}
                </p>

                <button
                  disabled={processing}
                  onClick={() => inputRef.current?.click()}
                  className="rounded-lg bg-silver px-6 py-3
                    text-sm font-semibold text-obsidian
                    hover:bg-offwhite"
                >
                  {file ? 'Change video' : 'Browse files'}
                </button>
              </div>

              {/* Generation settings */}
              <div className="mt-6 rounded-xl border
                border-steel bg-graphite p-6">
                <h3 className="mb-5 font-display text-lg font-semibold">
                  Generation settings
                </h3>

                <div className="grid gap-3 sm:grid-cols-2">
                  {([
                    {
                      value: 'keywords',
                      label: 'Standard engine',
                      description: 'Local keyword-based scoring',
                      icon: Cpu,
                    },
                    {
                      value: 'ai',
                      label: 'AI engine',
                      description: 'Advanced semantic scoring',
                      icon: Sparkles,
                    },
                  ] as const).map(option => (
                    <button
                      key={option.value}
                      disabled={processing}
                      onClick={() => setMode(option.value)}
                      className={`rounded-lg border p-4 text-left
                        ${mode === option.value
                          ? 'border-nardo bg-carbon'
                          : 'border-steel hover:bg-carbon'
                        }`}
                    >
                      <option.icon size={20} className="mb-3 text-nardo" />
                      <p className="text-sm font-semibold">{option.label}</p>
                      <p className="mt-1 text-xs text-muted">
                        {option.description}
                      </p>
                    </button>
                  ))}
                </div>

                <p className="mt-4 text-xs text-muted">
                  Up to 5 clips · 10–60 seconds · 9:16 · Subtitles
                </p>

                <button
                  disabled={!file || processing || !online}
                  onClick={generate}
                  className="mt-6 flex w-full items-center
                    justify-center gap-2 rounded-lg bg-silver
                    py-3 text-sm font-semibold text-obsidian
                    hover:bg-offwhite"
                >
                  {processing
                    ? <LoaderCircle size={18} className="animate-spin" />
                    : <Sparkles size={18} />}
                  {processing ? 'Generating...' : 'Generate clips'}
                </button>
              </div>

              {/* Statistics */}
              <div className="mt-8 grid gap-4 sm:grid-cols-3">
                {[
                  { label: 'Projects', value: projects.length, icon: FolderOpen },
                  { label: 'Clips generated', value: allClips.length, icon: Film },
                  { label: 'Content generated', value: `${Math.round(totalDuration)}s`, icon: Clock },
                ].map(stat => (
                  <div key={stat.label} className="rounded-xl
                    border border-steel bg-graphite p-5">
                    <stat.icon size={20} className="mb-4 text-nardo" />
                    <p className="text-xs text-muted">{stat.label}</p>
                    <p className="mt-2 font-display text-3xl font-semibold">
                      {stat.value}
                    </p>
                  </div>
                ))}
              </div>
            </motion.div>
          )}

          {page === 'Projects' && (
            <div>
              <h2 className="mb-8 font-display text-3xl font-semibold">
                Your projects
              </h2>

              {projects.length === 0 && (
                <div className="rounded-xl border border-steel
                  p-16 text-center text-muted">
                  No projects yet.
                </div>
              )}

              <div className="space-y-3">
                {projects.map(project => (
                  <div key={project.result.job_id}
                    className="flex items-center justify-between
                      rounded-xl border border-steel bg-graphite p-5">
                    <div className="flex items-center gap-4">
                      <FolderOpen className="text-nardo" />
                      <div>
                        <p className="font-medium">{project.name}</p>
                        <p className="mt-1 text-xs text-muted">
                          {project.result.clips.length} clips generated
                        </p>
                      </div>
                    </div>

                    <button
                      onClick={() => setPage('My clips')}
                      aria-label="View clips"
                    >
                      <ArrowUpRight size={20} />
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}

          {page === 'My clips' && (
            <div>
              <h2 className="font-display text-3xl font-semibold">
                Your clips
              </h2>

              <p className="mb-8 mt-2 text-sm text-muted">
                {allClips.length} clips generated
              </p>

              {allClips.length === 0 && (
                <div className="rounded-xl border border-steel
                  p-16 text-center text-muted">
                  No clips available yet.
                </div>
              )}

              <div className="grid gap-6 sm:grid-cols-2 xl:grid-cols-3">
                {allClips.map(clip => (
                  <div
                    key={clip.download_url}
                    className="overflow-hidden rounded-xl
                      border border-steel bg-graphite"
                  >
                    <video
                      src={getClipUrl(clip.download_url)}
                      controls
                      preload="metadata"
                      className="aspect-[9/16] w-full bg-black object-contain"
                    />

                    <div className="p-4">
                      <div className="mb-3 flex justify-between text-xs">
                        <span className="text-nardo">
                          {clip.duration.toFixed(1)}s
                        </span>
                        <span>Score: {clip.score}</span>
                      </div>

                      <p className="mb-4 line-clamp-3 text-sm text-silver">
                        {clip.text}
                      </p>

                      <div className="flex gap-2">
                        <button
                          onClick={() => setSelectedClip(clip)}
                          className="flex-1 rounded-lg border
                            border-steel py-2 text-xs hover:bg-carbon"
                        >
                          Details
                        </button>

                        <a
                          href={getClipUrl(clip.download_url)}
                          download
                          className="flex flex-1 items-center justify-center
                            gap-2 rounded-lg bg-silver py-2
                            text-xs font-semibold text-obsidian"
                        >
                          <Download size={14} />
                          Export
                        </a>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

        </div>
      </main>

      {/* Clip details */}
      {selectedClip && (
        <div className="fixed inset-0 z-50 flex items-center
          justify-center bg-black/80 p-5 backdrop-blur-sm">

          <div className="max-h-[90vh] w-full max-w-lg
            overflow-y-auto rounded-xl border border-steel
            bg-graphite p-6">

            <div className="mb-5 flex items-center justify-between">
              <h3 className="font-display text-xl font-semibold">
                Clip details
              </h3>
              <button onClick={() => setSelectedClip(null)}>
                <X size={20} />
              </button>
            </div>

            <video
              src={getClipUrl(selectedClip.download_url)}
              controls
              className="mx-auto max-h-[45vh] rounded-lg"
            />

            <div className="my-5 grid grid-cols-3 gap-3 text-sm">
              <div>Start: {selectedClip.start.toFixed(1)}s</div>
              <div>End: {selectedClip.end.toFixed(1)}s</div>
              <div>Score: {selectedClip.score}</div>
            </div>

            <p className="text-sm leading-relaxed text-silver">
              {selectedClip.text}
            </p>
          </div>
        </div>
      )}
    </div>
  )
}

export default App
