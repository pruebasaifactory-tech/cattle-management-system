import { Component } from "@angular/core";
import { Router } from "@angular/router";
import { AuthService } from "../../shared/services/auth.service";

@Component({
  selector: "app-login",
  template: `
    <div class="login-container">
      <div class="login-card card">
        <h2>🐄 Iniciar Sesión</h2>
        <form (ngSubmit)="onSubmit()">
          <div class="form-group">
            <label>Email</label>
            <input 
              type="email" 
              [(ngModel)]="email" 
              name="email"
              class="form-control"
              required
              placeholder="usuario@ejemplo.com"
            >
          </div>
          <div class="form-group">
            <label>Contraseña</label>
            <input 
              type="password" 
              [(ngModel)]="password" 
              name="password"
              class="form-control"
              required
              placeholder="••••••••"
            >
          </div>
          <button type="submit" class="btn btn-primary btn-block" [disabled]="loading">
            {{ loading ? "Ingresando..." : "Ingresar" }}
          </button>
          <div *ngIf="error" class="error-message">
            {{ error }}
          </div>
        </form>
        <div class="demo-info">
          <p><strong>Demo:</strong> Registra un usuario o usa credenciales de prueba</p>
          <button class="btn-link" (click)="showRegister = !showRegister">
            {{ showRegister ? "Ya tengo cuenta" : "Crear cuenta nueva" }}
          </button>
        </div>
        
        <div *ngIf="showRegister" class="register-form">
          <h3>Registro</h3>
          <form (ngSubmit)="onRegister()">
            <div class="form-group">
              <label>Nombre</label>
              <input 
                type="text" 
                [(ngModel)]="registerData.nombre" 
                name="nombre"
                class="form-control"
                required
              >
            </div>
            <div class="form-group">
              <label>Email</label>
              <input 
                type="email" 
                [(ngModel)]="registerData.email" 
                name="reg_email"
                class="form-control"
                required
              >
            </div>
            <div class="form-group">
              <label>Contraseña</label>
              <input 
                type="password" 
                [(ngModel)]="registerData.password" 
                name="reg_password"
                class="form-control"
                required
                minlength="8"
              >
            </div>
            <button type="submit" class="btn btn-primary btn-block">
              Registrar
            </button>
          </form>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .login-container {
      display: flex;
      justify-content: center;
      align-items: center;
      min-height: calc(100vh - 100px);
      padding: 20px;
    }
    .login-card {
      width: 100%;
      max-width: 400px;
    }
    .login-card h2 {
      text-align: center;
      margin-bottom: 2rem;
      color: #2c3e50;
    }
    .form-group {
      margin-bottom: 1.5rem;
    }
    .form-group label {
      display: block;
      margin-bottom: 0.5rem;
      font-weight: 500;
    }
    .form-control {
      width: 100%;
      padding: 0.75rem;
      border: 1px solid #ddd;
      border-radius: 4px;
      font-size: 14px;
    }
    .form-control:focus {
      outline: none;
      border-color: #3498db;
    }
    .btn-block {
      width: 100%;
      padding: 0.75rem;
      font-size: 16px;
    }
    .btn-block:disabled {
      opacity: 0.6;
      cursor: not-allowed;
    }
    .error-message {
      margin-top: 1rem;
      padding: 0.75rem;
      background: #fee;
      border: 1px solid #fcc;
      border-radius: 4px;
      color: #c33;
      text-align: center;
    }
    .demo-info {
      margin-top: 1.5rem;
      padding: 1rem;
      background: #f8f9fa;
      border-radius: 4px;
      text-align: center;
      font-size: 0.9rem;
    }
    .btn-link {
      background: none;
      border: none;
      color: #3498db;
      cursor: pointer;
      text-decoration: underline;
      margin-top: 0.5rem;
    }
    .register-form {
      margin-top: 2rem;
      padding-top: 2rem;
      border-top: 1px solid #ddd;
    }
    .register-form h3 {
      margin-bottom: 1rem;
      color: #2c3e50;
    }
  `]
})
export class LoginComponent {
  email = "";
  password = "";
  error = "";
  loading = false;
  showRegister = false;
  registerData = {
    nombre: "",
    email: "",
    password: ""
  };

  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  onSubmit(): void {
    if (!this.email || !this.password) {
      this.error = "Por favor ingrese email y contraseña";
      return;
    }

    this.loading = true;
    this.error = "";

    this.authService.login(this.email, this.password).subscribe({
      next: () => {
        this.router.navigate(["/dashboard"]);
      },
      error: (err) => {
        this.error = err.error?.detail || "Error al iniciar sesión";
        this.loading = false;
      }
    });
  }

  onRegister(): void {
    if (!this.registerData.nombre || !this.registerData.email || !this.registerData.password) {
      this.error = "Por favor complete todos los campos";
      return;
    }

    this.authService.register(
      this.registerData.nombre,
      this.registerData.email,
      this.registerData.password
    ).subscribe({
      next: () => {
        // Auto login después de registro
        this.email = this.registerData.email;
        this.password = this.registerData.password;
        this.showRegister = false;
        this.onSubmit();
      },
      error: (err) => {
        this.error = err.error?.detail || "Error al registrar usuario";
      }
    });
  }
}
