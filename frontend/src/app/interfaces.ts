export interface Execution {
  id: number;
  bot_id: number;
  status: 'pending' | 'working' | 'completed' | 'failed';
  log_text: string;
  started_at: string;
  finished_at?: string;
  screenshot_url?: string; // El signo ? significa que es opcional
}