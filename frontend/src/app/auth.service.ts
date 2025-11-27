import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

// @Injectable: Este decorador le dice a Angular:
// "Oye, esta clase es un Servicio. Prepárala para ser inyectada en cualquier componente que la pida".
@Injectable({
  providedIn: 'root', // 'root' significa que hay una sola instancia de este servicio para toda la app (Singleton).
})
export class AuthService {
  // Definimos la URL de tu API de Python (Docker se encarga de redirigir esto)
  // Nota: En desarrollo local usamos localhost:8000
  private apiUrl = 'http://localhost:8000';

  // Constructor: Aquí pedimos las herramientas que necesitamos.
  // Angular nos da automáticamente una instancia de 'HttpClient' lista para usar.
  constructor(private http: HttpClient) {}

  // Función para hacer Login
  // Recibe email y password, y retorna un "Observable" (una promesa de que vendrán datos en el futuro)
  login(email: string, password: string): Observable<any> {
    // Preparamos los datos del formulario (como lo requiere OAuth2 en Python)
    const formData = new FormData();
    formData.append('username', email); // En OAuth2 el campo se llama 'username' aunque sea email
    formData.append('password', password);

    // Hacemos la petición POST
    // Es equivalente a: requests.post(url, data=formData) en Python
    return this.http.post(`${this.apiUrl}/auth/login`, formData);
  }
}
