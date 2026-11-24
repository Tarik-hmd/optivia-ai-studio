
import axios from 'axios'

export const API_URL = 'http://127.0.0.1:8000'

export type ProcessingMode = 'keywords' | 'ai'

export interface Clip {
  text: string
  start: number
  end: number
  duration: number
  score: number
  word_count: number
  download_url: string
}

export interface ProcessingResult {
  job_id: string
  transcription: {
    text: string
    language?: string
  }
  clips: Clip[]
}

export async function checkHealth(): Promise<boolean> {
  try {
    const response = await axios.get(`${API_URL}/health`, {
      timeout: 3000,
    })
    return response.data.status === 'ok'
  } catch {
    return false
  }
}

export async function processVideo(
  file: File,
  mode: ProcessingMode
): Promise<ProcessingResult> {
  const formData = new FormData()

  formData.append('file', file)
  formData.append('mode', mode)

  const response = await axios.post<ProcessingResult>(
    `${API_URL}/process-video`,
    formData
  )

  return response.data
}

export function getClipUrl(path: string): string {
  return `${API_URL}${path}`
}
