import { Component, OnInit } from "@angular/core";
import { CattleService, Cattle } from "../../shared/services/cattle.service";

@Component({
  selector: "app-dashboard",
  template: `
    <div class="dashboard">
      <h2>Dashboard</h2>
      
      <div class="stats-grid">
        <div class="stat-card card">
          <div class="stat-icon">🐄</div>
          <h3>{{ stats.totalCattle }}</h3>
          <p>Total Ganado</p>
        </div>
        <div class="stat-card card">
          <div class="stat-icon">✅</div>
          <h3>{{ stats.healthyCount }}</h3>
          <p>Saludables</p>
        </div>
        <div class="stat-card card">
          <div class="stat-icon">🏥</div>
          <h3>{{ stats.sickCount }}</h3>
          <p>Enfermas</p>
        </div>
        <div class="stat-card card">
          <div class="stat-icon">⚖️</div>
          <h3>{{ stats.avgWeight }} kg</h3>
          <p>Peso Promedio</p>
        </div>
      </div>

      <div class="recent-section">
        <h3>Ganado Reciente</h3>
        <div class="card">
          <table *ngIf="recentCattle.length > 0">
            <thead>
              <tr>
                <th>ID</th>
                <th>Nombre</th>
                <th>Raza</th>
                <th>Estado</th>
              </tr>
            </thead>
            <tbody>
              <tr *ngFor="let cattle of recentCattle">
                <td>{{ cattle.identificador }}</td>
                <td>{{ cattle.nombre }}</td>
                <td>{{ cattle.raza || "-" }}</td>
                <td>
                  <span class="status-badge" [class]="cattle.estado">
                    {{ cattle.estado }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
          <div *ngIf="recentCattle.length === 0" class="no-data">
            No hay registros todavía
          </div>
        </div>
      </div>

      <div class="actions">
        <button class="btn btn-primary" routerLink="/cattle">
          Ver Listado Completo
        </button>
      </div>
    </div>
  `,
  styles: [`
    .dashboard {
      padding: 2rem 0;
    }
    h2 {
      margin-bottom: 2rem;
      color: #2c3e50;
    }
    .stats-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
      gap: 1.5rem;
      margin-bottom: 3rem;
    }
    .stat-card {
      text-align: center;
      padding: 2rem;
      transition: transform 0.2s;
    }
    .stat-card:hover {
      transform: translateY(-4px);
    }
    .stat-icon {
      font-size: 3rem;
      margin-bottom: 1rem;
    }
    .stat-card h3 {
      font-size: 2.5rem;
      color: #3498db;
      margin: 0.5rem 0;
    }
    .stat-card p {
      color: #7f8c8d;
      font-size: 1.1rem;
      margin: 0;
    }
    .recent-section h3 {
      margin-bottom: 1rem;
      color: #2c3e50;
    }
    table {
      width: 100%;
      border-collapse: collapse;
    }
    table th,
    table td {
      padding: 12px;
      text-align: left;
      border-bottom: 1px solid #ecf0f1;
    }
    table th {
      background: #f8f9fa;
      font-weight: 600;
    }
    .status-badge {
      padding: 0.25rem 0.75rem;
      border-radius: 12px;
      font-size: 0.85rem;
      font-weight: 500;
    }
    .status-badge.activa {
      background: #d4edda;
      color: #155724;
    }
    .status-badge.enferma {
      background: #fff3cd;
      color: #856404;
    }
    .no-data {
      text-align: center;
      padding: 2rem;
      color: #7f8c8d;
    }
    .actions {
      text-align: center;
      margin-top: 2rem;
    }
  `]
})
export class DashboardComponent implements OnInit {
  stats = {
    totalCattle: 0,
    healthyCount: 0,
    sickCount: 0,
    avgWeight: 0
  };
  
  recentCattle: Cattle[] = [];

  constructor(private cattleService: CattleService) {}

  ngOnInit(): void {
    this.loadDashboardData();
  }

  loadDashboardData(): void {
    this.cattleService.getAll().subscribe({
      next: (cattle) => {
        this.stats.totalCattle = cattle.length;
        this.stats.healthyCount = cattle.filter(c => c.estado === "activa").length;
        this.stats.sickCount = cattle.filter(c => c.estado === "enferma").length;
        
        const weights = cattle
          .filter(c => c.peso_actual !== null)
          .map(c => c.peso_actual!);
        
        if (weights.length > 0) {
          this.stats.avgWeight = Math.round(
            weights.reduce((a, b) => a + b, 0) / weights.length
          );
        }
        
        this.recentCattle = cattle.slice(0, 5);
      },
      error: (err) => {
        console.error("Error loading dashboard data:", err);
      }
    });
  }
}
