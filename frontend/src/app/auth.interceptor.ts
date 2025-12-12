import { HttpInterceptorFn, HttpErrorResponse } from '@angular/common/http';
import { inject } from '@angular/core';
import { catchError, throwError } from 'rxjs';

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  
  return next(req).pipe(
    catchError((error: HttpErrorResponse) => {
      // Si el error es 401 (Unauthorized), significa que el token venció o es falso
      if (error.status === 401) {
        console.warn('⚠️ Sesión caducada. Cerrando sesión...');
        
        // 1. Borramos el rastro del usuario
        localStorage.removeItem('user_token');
        localStorage.removeItem('user_email');

        // 2. Recargamos la página. 
        // Al recargar, AppComponent ejecutará ngOnInit, verá que no hay token 
        // y mostrará automáticamente la pantalla de Login.
        window.location.reload();
      }
      
      // Si es otro error, dejamos que siga su camino
      return throwError(() => error);
    })
  );
};