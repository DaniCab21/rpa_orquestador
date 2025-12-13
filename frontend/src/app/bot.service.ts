import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders, HttpParams } from '@angular/common/http';
import { Observable, Subject } from 'rxjs';
import { Execution } from './interfaces';

@Injectable({ providedIn: 'root' })
export class BotService {
  private apiUrl = 'http://localhost:8000';
  private socket: WebSocket | undefined;
  // Usamos un Subject para que el componente se suscriba a los mensajes
  public messages$ = new Subject<any>();

  constructor(private http: HttpClient) {}

  // Obtener headers con el token (Método auxiliar)
  private getHeaders(token: string): HttpHeaders {
    return new HttpHeaders({ Authorization: `Bearer ${token}` });
  }

  // 1. Obtener lista de bots
  getBots(token: string): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/bots/`, {
      headers: this.getHeaders(token),
    });
  }

  // 2. Ejecutar un bot
  executeBot(token: string, botName: string, url: string): Observable<any> {
    // Nota: Enviamos 'url' como query param (?url=...)
    return this.http.post<any>(
      `${this.apiUrl}/executions/${botName}?url=${encodeURIComponent(url)}`,
      {}, // Cuerpo vacío (body)
      { headers: this.getHeaders(token) }
    );
  }

  // 3. Crear Bot
  createBot(token: string, botData: any): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/bots/`, botData, {
      headers: this.getHeaders(token),
    });
  }

  // 4. Eliminar Bot
  deleteBot(token: string, botId: number): Observable<any> {
    return this.http.delete<any>(`${this.apiUrl}/bots/${botId}`, {
      headers: this.getHeaders(token),
    });
  }

  // (Opcional por ahora) Editar Bot
  updateBot(token: string, botId: number, botData: any): Observable<any> {
    return this.http.patch<any>(`${this.apiUrl}/bots/${botId}`, botData, {
      headers: this.getHeaders(token),
    });
  }

  // 5. Obtener estadísticas
  getStats(token: string): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/bots/stats/overview`, {
      headers: this.getHeaders(token),
    });
  }

  connectWebSocket() {
    // Asegúrate de que la URL coincida con tu backend (ws:// en vez de http://)
    this.socket = new WebSocket('ws://localhost:8000/ws');

    this.socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log('⚡ Notificación recibida:', data);
      this.messages$.next(data); // Avisamos a quien esté escuchando
    };

    this.socket.onclose = () => {
      console.warn('WebSocket desconectado. Reintentando en 3s...');
      setTimeout(() => this.connectWebSocket(), 3000);
    };
  }

  getExecutions(token: string, botId: number): Observable<Execution[]> {
    const headers = { Authorization: `Bearer ${token}` };

    // Configuramos los filtros en la URL (?bot_id=X)
    const params = new HttpParams().set('bot_id', botId.toString());

    return this.http.get<Execution[]>(`${this.apiUrl}/executions/`, { headers, params });
  }
}
