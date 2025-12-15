import { Component, OnInit } from '@angular/core'; // <--- Agregado OnInit
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { AuthService } from './auth.service';
import { BotService } from './bot.service';
import { ChangeDetectorRef } from '@angular/core';
import { Execution } from './interfaces';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [FormsModule, CommonModule],
  templateUrl: './app.html',
  styleUrl: './app.scss',
})
export class AppComponent implements OnInit {
  // Variables de Login
  email: string = '';
  password: string = '';
  token: string | null = null;
  errorMessage: string = '';
  currentUserEmail: string = '';

  // Variables de Dashboard
  bots: any[] = [];
  targetUrl: string = 'https://www.wikipedia.org';
  executionMessage: string = '';

  // Variables para crear nuevo bot
  newBotName: string = '';
  newBotDescription: string = '';

  // Variable para controlar formulario
  isRegistering: boolean = false;

  // KPIs
  stats = {
    total: 0,
    by_status: {
      idle: 0,
      working: 0,
      completed: 0,
      failed: 0,
    },
  };

  // 👇 VARIABLES NUEVAS PARA EL HISTORIAL
  showHistoryModal: boolean = false;
  historyLoading: boolean = false;
  selectedBotName: string = '';
  executions: Execution[] = [];

  constructor(
    private authService: AuthService,
    private botService: BotService,
    private cd: ChangeDetectorRef
  ) {}

  ngOnInit() {
    // 1. RECUPERAR SESIÓN (Persistencia al dar F5)
    const savedToken = localStorage.getItem('user_token');
    const savedEmail = localStorage.getItem('user_email');

    if (savedToken) {
      this.token = savedToken;
      if (savedEmail) this.currentUserEmail = savedEmail;

      // Reactivamos el temporizador de seguridad
      this.authService.setAutoLogoutTimer(savedToken);

      // Cargamos datos y conectamos socket
      this.loadBots();
      this.loadStats();
      this.botService.connectWebSocket();
    }

    // 2. SUSCRIPCIÓN A WEBSOCKETS (Escuchar cambios en tiempo real)
    this.botService.messages$.subscribe((update: any) => {
      // update trae { bot_name, status, last_analysis, last_analysis_at }

      const botIndex = this.bots.findIndex((b) => b.name === update.bot_name);
      if (botIndex !== -1) {
        // Actualizamos SOLO el bot que cambió
        this.bots[botIndex].status = update.status;
        this.bots[botIndex].last_analysis = update.last_analysis;
        this.bots[botIndex].last_analysis_at = update.last_analysis_at;

        // Actualizamos estadísticas también para que cuadren los números
        this.loadStats();

        // Magia visual: Forzamos la detección de cambios
        this.cd.detectChanges();

        // Si hay un mensaje de "Enviando orden...", lo cambiamos a finalizado
        if (this.executionMessage.includes(update.bot_name)) {
          this.executionMessage = `🏁 ¡${update.bot_name} finalizó!`;
          setTimeout(() => {
            this.executionMessage = '';
            this.cd.detectChanges();
          }, 3000);
          this.cd.detectChanges();
        }
      }
    });
  }

  // --- LÓGICA DE AUTENTICACIÓN ---

  private cleanForm() {
    this.email = '';
    this.password = '';
    this.errorMessage = '';
  }

  toggleAuthMode(isRegistering: boolean) {
    this.isRegistering = isRegistering;
    this.cleanForm();
  }

  onRegister() {
    if (!this.email.trim() || !this.password.trim()) {
      this.errorMessage = '⚠️ Por favor, completa todos los campos.';
      return;
    }
    if (this.password.length < 4) {
      this.errorMessage = '⚠️ La contraseña debe tener al menos 4 caracteres.';
      return;
    }
    this.authService.register(this.email, this.password).subscribe({
      next: (res) => {
        this.errorMessage = '';
        alert('🆗 ¡Cuenta creada con éxito! Ahora puedes iniciar sesión.');
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
        // Guardamos variables locales
        this.token = response.access_token;
        this.currentUserEmail = this.email;
        this.errorMessage = '';

        // GUARDAMOS EN LOCALSTORAGE (Persistencia)
        localStorage.setItem('user_token', this.token!);
        localStorage.setItem('user_email', this.email);

        // ACTIVAMOS TEMPORIZADOR DE AUTO-LOGOUT
        this.authService.setAutoLogoutTimer(this.token!);

        // Iniciamos la app
        this.loadBots();
        this.loadStats();
        this.botService.connectWebSocket();
        this.cleanForm();
      },
      error: (error) => {
        this.errorMessage = 'Por favor valide las credenciales e intente nuevamente';
        this.cd.detectChanges();
      },
    });
  }

  logout() {
    // Delegamos al servicio para que limpie token, timer y localStorage
    this.authService.logout();
    // Limpiamos variables locales por si acaso
    this.token = null;
    this.bots = [];
    this.executionMessage = '';
  }

  onSubmit() {
    if (this.isRegistering) {
      this.onRegister();
    } else {
      this.onLogin();
    }
  }

  // --- LÓGICA DE BOTS ---

  loadBots() {
    if (!this.token) return;
    this.botService.getBots(this.token).subscribe({
      next: (data) => {
        this.bots = data;
        this.cd.detectChanges();
      },
      error: (err) => console.error('Error cargando bots', err),
    });
  }

  loadStats() {
    if (!this.token) return;
    this.botService.getStats(this.token).subscribe({
      next: (data) => {
        this.stats = data;
        this.cd.detectChanges();
      },
      error: (err) => console.error('Error cargando stats', err),
    });
  }

  runBot(botName: string) {
    if (!this.token) return;
    this.executionMessage = `Enviando orden a ${botName}...`;

    // Feedback visual inmediato (opcional)
    const bot = this.bots.find((b) => b.name === botName);
    if (bot) bot.status = 'working';
    this.cd.detectChanges();

    this.botService.executeBot(this.token, botName, this.targetUrl).subscribe({
      next: (res) => {
        this.executionMessage = `✅ ¡Orden recibida! ID Tarea: ${res.task_id}`;
        this.cd.detectChanges();
        // Nota: Ya no usamos setTimeout para borrar el mensaje aquí,
        // dejamos que el WebSocket lo borre al terminar la tarea.
      },
      error: (err) => {
        this.executionMessage = `❌ Error: ${err.message}`;
        if (bot) bot.status = 'failed';
        this.cd.detectChanges();
      },
    });
  }

  createBot() {
    if (!this.token) return;
    const newBot = {
      name: this.newBotName,
      description: this.newBotDescription,
      status: 'idle',
    };

    if (!newBot.name.trim() || !newBot.description.trim()) {
      this.executionMessage = '⚠️ Por favor, completa todos los campos.';
      this.cd.detectChanges();
      return;
    }

    this.botService.createBot(this.token, newBot).subscribe({
      next: (res) => {
        this.executionMessage = `✅ Bot '${res.name}' creado exitosamente`;
        this.newBotName = '';
        this.newBotDescription = '';
        this.loadBots();
        this.loadStats();
        setTimeout(() => {
          this.executionMessage = '';
          this.cd.detectChanges();
        }, 3000);
      },
      error: (err) => {
        this.executionMessage = '❌ Error creando bot';
        this.cd.detectChanges();
      },
    });
  }

  deleteBot(botId: number) {
    if (!confirm('¿Estás seguro de que quieres eliminar este bot?')) return;
    if (!this.token) return;

    this.botService.deleteBot(this.token, botId).subscribe({
      next: () => {
        this.executionMessage = '🗑️ Bot eliminado';
        this.loadBots();
        this.loadStats();
        this.cd.detectChanges();
        setTimeout(() => {
          this.executionMessage = '';
          this.cd.detectChanges();
        }, 3000);
      },
      error: (err) => {
        this.executionMessage = '❌ Error eliminando bot';
        this.cd.detectChanges();
      },
    });
  }

  toggleExpand(bot: any) {
    bot.isExpanded = !bot.isExpanded;
    this.cd.detectChanges();
  }

  // 👇 FUNCIÓN PARA ABRIR EL HISTORIAL
  viewHistory(bot: any) {
    if (!this.token) return;

    this.selectedBotName = bot.name;
    this.showHistoryModal = true;
    this.historyLoading = true;
    this.executions = []; // Limpiar datos viejos

    this.cd.detectChanges();

    this.botService.getExecutions(this.token, bot.id).subscribe({
      next: (data) => {
        this.executions = data;
        this.historyLoading = false;
        this.cd.detectChanges();
      },
      error: (err) => {
        console.error('Error cargando historial', err);
        this.historyLoading = false;
        this.cd.detectChanges();
      },
    });
  }

  // 👇 FUNCIÓN PARA CERRAR
  closeHistory() {
    this.showHistoryModal = false;
  }
}
