import { ApplicationConfig, provideZoneChangeDetection } from '@angular/core';
import { provideRouter } from '@angular/router';
import { routes } from './app.routes';
// 1. Importa 'withInterceptors' y tu interceptor creado
import { provideHttpClient, withFetch, withInterceptors } from '@angular/common/http';
import { authInterceptor } from './auth.interceptor'; // <--- IMPORTAR ESTO

export const appConfig: ApplicationConfig = {
  providers: [
    provideZoneChangeDetection({ eventCoalescing: true }),
    provideRouter(routes),

    // 2. Modifica esta línea para inyectar el interceptor
    provideHttpClient(
      withFetch(),
      withInterceptors([authInterceptor]) // <--- AGREGAR ESTO AQUÍ
    ),
  ],
};
