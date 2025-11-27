import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class BotService {
  private apiUrl = 'http://localhost:8000';

  constructor(private http: HttpClient) { }

  // Obtener headers con el token (Método auxiliar)
  private getHeaders(token: string): HttpHeaders {
    return new HttpHeaders({
      'Authorization': `Bearer ${token}`
    });
  }

  // 1. Obtener lista de bots
  getBots(token: string): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/bots/`, { 
      headers: this.getHeaders(token) 
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
}