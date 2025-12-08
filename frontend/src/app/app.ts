import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { AuthService } from './auth.service';
import { BotService } from './bot.service';
// import { ChangeDetectorRef } from '@angular/core'; // <--- Agrega ChangeDetectorRef
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

  // Variables para crear nuevo bot
  newBotName: string = '';
  newBotDescription: string = '';

  // Variable para guardar los KPIs (Inicializamos con ceros)
  stats = {
    total: 0,
    by_status: {
      idle: 0,
      working: 0,
      completed: 0,
      failed: 0,
    },
  };

  // Inyectamos ambos servicios
  constructor(
    private authService: AuthService,
    private botService: BotService // private cd: ChangeDetectorRef
  ) {}

  private cleanForm() {
    this.email = '';
    this.password = '';
    this.errorMessage = '';
  }

  toggleAuthMode(isRegistering: boolean) {
    this.isRegistering = isRegistering;
    this.cleanForm(); // <--- ¡Aquí está el truco! Limpiamos al cambiar
  }
  // Variable para controlar qué formulario mostramos
  isRegistering: boolean = false;
  // Función para registrar
  onRegister() {
    // 1. VALIDACIÓN SIMPLE
    // .trim() elimina espacios en blanco al inicio y final
    if (!this.email.trim() || !this.password.trim()) {
      this.errorMessage = '⚠️ Por favor, completa todos los campos.';
      return; // <--- AQUÍ DETENEMOS TODO
    }

    if (this.password.length < 4) {
      this.errorMessage = '⚠️ La contraseña debe tener al menos 4 caracteres.';
      return;
    }
    this.authService.register(this.email, this.password).subscribe({
      next: (res) => {
        // Si el registro es exitoso:
        this.errorMessage = '';
        alert('¡Cuenta creada con éxito! Ahora puedes iniciar sesión.');
        // this.isRegistering = false; // Volvemos al Login automáticamente
        this.toggleAuthMode(false);
      },
      error: (err) => {
        console.error(err);
        this.errorMessage = 'Error al registrar. El email podría estar duplicado.';
      },
    });
  }

  onLogin() {
    if (!this.email.trim() || !this.password.trim()) {
      this.errorMessage = 'Ingresa tu email y contraseña.';
      return;
    }
    this.authService.login(this.email, this.password).subscribe({
      next: (response) => {
        this.token = response.access_token;
        this.errorMessage = '';
        // ¡IMPORTANTE! Apenas nos logueamos, cargamos los bots
        this.loadBots();
        this.loadStats();
        this.cleanForm();
      },
      error: (error) => {
        console.error('ERROR: ' + error);
        this.errorMessage = 'Por favor valide las credenciales e intente nuevamente';
      },
    });
  }

  // Función para pedir los bots a la API
  loadBots() {
    if (!this.token) return;

    this.botService.getBots(this.token).subscribe({
      next: (data) => {
        this.bots = data;
        // this.cd.detectChanges();
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

  // FUNCIÓN NUEVA: Crear Bot
  createBot() {
    if (!this.token) return;

    const newBot = {
      name: this.newBotName,
      description: this.newBotDescription,
      status: 'idle',
    };

    this.botService.createBot(this.token, newBot).subscribe({
      next: (res) => {
        this.executionMessage = `✅ Bot '${res.name}' creado exitosamente`;
        // Limpiamos el formulario
        this.newBotName = '';
        this.newBotDescription = '';
        // Recargamos la lista para que aparezca el nuevo
        this.loadBots();
        this.loadStats();
      },
      error: (err) => (this.executionMessage = '❌ Error creando bot'),
    });
  }

  // FUNCIÓN NUEVA: Borrar Bot
  deleteBot(botId: number) {
    if (!confirm('¿Estás seguro de que quieres eliminar este bot?')) return;

    if (!this.token) return;

    this.botService.deleteBot(this.token, botId).subscribe({
      next: () => {
        this.executionMessage = '🗑️ Bot eliminado';
        this.loadBots(); // Recargar lista
        this.loadStats();
      },
      error: (err) => (this.executionMessage = '❌ Error eliminando bot'),
    });
  }

  // FUNCIÓN NUEVA
  loadStats() {
    if (!this.token) return;
    this.botService.getStats(this.token).subscribe({
      next: (data) => {
        this.stats = data;
        // this.cd.detectChanges();
      },
      error: (err) => console.error('Error cargando stats', err),
    });
  }

  logout() {
    this.token = null;
    this.bots = [];
    this.executionMessage = '';
    this.cleanForm();
  }

  onSubmit() {
    if (this.isRegistering) {
      this.onRegister();
    } else {
      this.onLogin();
    }
  }
}
