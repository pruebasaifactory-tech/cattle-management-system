import { Component } from "@angular/core";

@Component({
  selector: "app-root",
  template: `
    <nav class="navbar">
      <h1>�� Sistema de Gestión de Ganado</h1>
      <div class="nav-links">
        <a routerLink="/login" *ngIf="!isLoggedIn()">Login</a>
        <a routerLink="/dashboard" *ngIf="isLoggedIn()">Dashboard</a>
        <a routerLink="/cattle" *ngIf="isLoggedIn()">Ganado</a>
        <button *ngIf="isLoggedIn()" (click)="logout()">Salir</button>
      </div>
    </nav>
    <div class="container">
      <router-outlet></router-outlet>
    </div>
  `,
  styles: [`
    .navbar {
      background: #2c3e50;
      color: white;
      padding: 1rem 2rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .navbar h1 {
      margin: 0;
      font-size: 1.5rem;
    }
    .nav-links {
      display: flex;
      gap: 1rem;
      align-items: center;
    }
    .nav-links a {
      color: white;
      text-decoration: none;
      padding: 0.5rem 1rem;
      border-radius: 4px;
      transition: background 0.3s;
    }
    .nav-links a:hover {
      background: rgba(255,255,255,0.1);
    }
    .nav-links button {
      background: #e74c3c;
      color: white;
      border: none;
      padding: 0.5rem 1rem;
      border-radius: 4px;
      cursor: pointer;
    }
  `]
})
export class AppComponent {
  isLoggedIn(): boolean {
    return !!localStorage.getItem("token");
  }

  logout(): void {
    localStorage.removeItem("token");
    window.location.href = "/login";
  }
}
