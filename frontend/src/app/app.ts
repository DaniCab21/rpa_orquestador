import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { AuthService } from './auth.service';
import { BotService } from './bot.service';
@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, FormsModule, CommonModule],
  templateUrl: './app.html',
  styleUrl: './app.scss',
})
export class AppComponent {
  // Variables de Login
  email: string = '';
  password: string = '';
  token: string | null = null;
  errorMessage: string = '';

  // Variables de Dashboard
  bots: any[] = []; // Lista de bots
  targetUrl: string = 'https://www.wikipedia.org'; // URL por defecto para ejecutar
  executionMessage: string = ''; // Mensaje de éxito al ejecutar

  // Inyectamos ambos servicios
  constructor(private authService: AuthService, private botService: BotService) {}

  onLogin() {
    this.authService.login(this.email, this.password).subscribe({
      next: (response) => {
        this.token = response.access_token;
        this.errorMessage = '';
        // ¡IMPORTANTE! Apenas nos logueamos, cargamos los bots
        this.loadBots();
      },
      error: (error) => {
        console.error(error);
        this.errorMessage = 'Credenciales incorrectas';
      },
    });
  }

  // Función para pedir los bots a la API
  loadBots() {
    if (!this.token) return;

    this.botService.getBots(this.token).subscribe({
      next: (data) => {
        this.bots = data;
      },
      error: (err) => console.error('Error cargando bots', err),
    });
  }

  // Función para disparar el worker
  runBot(botName: string) {
    if (!this.token) return;
    this.executionMessage = `Enviando orden a ${botName}...`;

    this.botService.executeBot(this.token, botName, this.targetUrl).subscribe({
      next: (res) => {
        this.executionMessage = `✅ ¡Orden recibida! ID Tarea: ${res.task_id}`;
        // Borramos el mensaje a los 5 segundos
        setTimeout(() => (this.executionMessage = ''), 5000);
      },
      error: (err) => {
        this.executionMessage = `❌ Error: ${err.message}`;
      },
    });
  }

  logout() {
    this.token = null;
    this.bots = [];
    this.executionMessage = '';
  }
}
