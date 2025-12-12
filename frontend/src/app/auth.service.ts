import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Router } from '@angular/router'; // Necesitamos el Router para redirigir

@Injectable({
  providedIn: 'root',
})
export class AuthService {
  private apiUrl = 'http://localhost:8000';
  private tokenTimer: any; // Aquí guardaremos la referencia al temporizador

  constructor(private http: HttpClient, private router: Router) {}

  login(email: string, password: string): Observable<any> {
    const formData = new FormData();
    formData.append('username', email);
    formData.append('password', password);

    return this.http.post(`${this.apiUrl}/auth/login`, formData);
  }

  register(email: string, password: string): Observable<any> {
    const body = { email: email, password: password };
    return this.http.post(`${this.apiUrl}/auth/signup`, body);
  }

  // --- NUEVA LÓGICA DE AUTO-LOGOUT ---

  // 1. Función pública para iniciar el conteo
  public setAutoLogoutTimer(token: string) {
    const expirationDate = this.getTokenExpiration(token);
    if (!expirationDate) return;

    const now = new Date();
    // Calculamos cuántos milisegundos faltan para que caduque
    const expiresIn = expirationDate.getTime() - now.getTime();

    if (expiresIn > 0) {
      console.log(`⏱️ Auto-logout programado en ${expiresIn / 1000} segundos.`);

      // Limpiamos cualquier timer anterior por seguridad
      if (this.tokenTimer) clearTimeout(this.tokenTimer);

      // Programamos la muerte de la sesión
      this.tokenTimer = setTimeout(() => {
        this.logout();
      }, expiresIn);
    } else {
      // Si ya expiró, cerramos inmediatamente
      this.logout();
    }
  }

  // 2. Función auxiliar para leer la fecha dentro del JWT (sin librerías externas)
  private getTokenExpiration(token: string): Date | null {
    try {
      // El JWT tiene 3 partes separadas por puntos. La segunda es el payload.
      const payloadBase64 = token.split('.')[1];
      // Decodificamos base64 y parseamos el JSON
      const payload = JSON.parse(atob(payloadBase64));

      if (payload && payload.exp) {
        // 'exp' viene en segundos, JS usa milisegundos, así que multiplicamos por 1000
        return new Date(payload.exp * 1000);
      }
      return null;
    } catch (e) {
      return null;
    }
  }

  // 3. Función Logout actualizada
  logout() {
    console.warn('👋 Cerrando sesión automáticamente...');
    this.tokenTimer = null;
    localStorage.removeItem('user_token');
    localStorage.removeItem('user_email');

    // Redirigimos al usuario (opcional recargar para limpiar estado)
    // this.router.navigate(['/']);
    window.location.reload();
  }
}
