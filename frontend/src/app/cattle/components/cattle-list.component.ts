import { Component, OnInit } from "@angular/core";
import { CattleService, Cattle, CattleCreate } from "../../shared/services/cattle.service";

@Component({
  selector: "app-cattle-list",
  template: `
    <div class="cattle-list">
      <div class="header">
        <h2>Listado de Ganado</h2>
        <button class="btn btn-primary" (click)="showAddForm = !showAddForm">
          {{ showAddForm ? "Cancelar" : "+ Agregar Vaca" }}
        </button>
      </div>
      
      <!-- Add Form -->
      <div *ngIf="showAddForm" class="card add-form">
        <h3>Nueva Vaca</h3>
        <form (ngSubmit)="onAddCattle()">
          <div class="form-row">
            <div class="form-group">
              <label>Identificador *</label>
              <input type="text" [(ngModel)]="newCattle.identificador" name="id" class="form-control" required>
            </div>
            <div class="form-group">
              <label>Nombre *</label>
              <input type="text" [(ngModel)]="newCattle.nombre" name="nombre" class="form-control" required>
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>Raza</label>
              <input type="text" [(ngModel)]="newCattle.raza" name="raza" class="form-control">
            </div>
            <div class="form-group">
              <label>Sexo *</label>
              <select [(ngModel)]="newCattle.sexo" name="sexo" class="form-control" required>
                <option value="H">Hembra</option>
                <option value="M">Macho</option>
              </select>
            </div>
            <div class="form-group">
              <label>Peso (kg)</label>
              <input type="number" [(ngModel)]="newCattle.peso_actual" name="peso" class="form-control">
            </div>
          </div>
          <div *ngIf="error" class="error-message">{{ error }}</div>
          <button type="submit" class="btn btn-primary" [disabled]="loading">
            {{ loading ? "Guardando..." : "Guardar" }}
          </button>
        </form>
      </div>

      <div class="card">
        <div class="filters">
          <input 
            type="text" 
            placeholder="Buscar por identificador o nombre..."
            [(ngModel)]="searchTerm"
            (input)="filterCattle()"
            class="search-input"
          >
          <select [(ngModel)]="statusFilter" (change)="loadCattle()" class="filter-select">
            <option value="">Todos los estados</option>
            <option value="activa">Activa</option>
            <option value="enferma">Enferma</option>
            <option value="vendida">Vendida</option>
          </select>
        </div>

        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Nombre</th>
              <th>Raza</th>
              <th>Sexo</th>
              <th>Peso (kg)</th>
              <th>Estado</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr *ngFor="let cattle of filteredCattle">
              <td>{{ cattle.identificador }}</td>
              <td>{{ cattle.nombre }}</td>
              <td>{{ cattle.raza || "-" }}</td>
              <td>{{ cattle.sexo === "H" ? "Hembra" : "Macho" }}</td>
              <td>{{ cattle.peso_actual || "-" }}</td>
              <td>
                <span class="status-badge" [class]="cattle.estado">
                  {{ cattle.estado }}
                </span>
              </td>
              <td>
                <button class="btn-small btn-danger" (click)="onDelete(cattle.id)">
                  Eliminar
                </button>
              </td>
            </tr>
          </tbody>
        </table>

        <div *ngIf="loading" class="loading">Cargando...</div>
        <div *ngIf="!loading && filteredCattle.length === 0" class="no-data">
          No se encontraron registros
        </div>
      </div>
    </div>
  `,
  styles: [`
    .cattle-list {
      padding: 2rem 0;
    }
    .header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 2rem;
    }
    .header h2 {
      margin: 0;
    }
    .add-form {
      margin-bottom: 2rem;
    }
    .add-form h3 {
      margin-bottom: 1.5rem;
      color: #2c3e50;
    }
    .form-row {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 1rem;
      margin-bottom: 1rem;
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
    .filters {
      display: flex;
      gap: 1rem;
      margin-bottom: 1.5rem;
    }
    .search-input {
      flex: 1;
      padding: 0.75rem;
      border: 1px solid #ddd;
      border-radius: 4px;
      font-size: 14px;
    }
    .filter-select {
      padding: 0.75rem;
      border: 1px solid #ddd;
      border-radius: 4px;
      font-size: 14px;
      min-width: 200px;
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
    .status-badge.vendida {
      background: #d1ecf1;
      color: #0c5460;
    }
    .btn-small {
      padding: 0.25rem 0.75rem;
      margin-right: 0.5rem;
      border: none;
      border-radius: 4px;
      cursor: pointer;
      font-size: 0.85rem;
    }
    .btn-danger {
      background: #e74c3c;
      color: white;
    }
    .btn-danger:hover {
      background: #c0392b;
    }
    .loading, .no-data {
      text-align: center;
      padding: 3rem;
      color: #7f8c8d;
    }
    .error-message {
      padding: 0.75rem;
      background: #fee;
      border: 1px solid #fcc;
      border-radius: 4px;
      color: #c33;
      margin-bottom: 1rem;
    }
  `]
})
export class CattleListComponent implements OnInit {
  cattleList: Cattle[] = [];
  filteredCattle: Cattle[] = [];
  searchTerm = "";
  statusFilter = "";
  loading = false;
  error = "";
  showAddForm = false;
  
  newCattle: CattleCreate = {
    identificador: "",
    nombre: "",
    sexo: "H"
  };

  constructor(private cattleService: CattleService) {}

  ngOnInit(): void {
    this.loadCattle();
  }

  loadCattle(): void {
    this.loading = true;
    this.cattleService.getAll(this.statusFilter).subscribe({
      next: (data) => {
        this.cattleList = data;
        this.filteredCattle = data;
        this.loading = false;
        this.filterCattle();
      },
      error: (err) => {
        console.error("Error loading cattle:", err);
        this.loading = false;
        this.error = "Error al cargar el ganado";
      }
    });
  }

  filterCattle(): void {
    this.filteredCattle = this.cattleList.filter(cattle => {
      const matchesSearch = !this.searchTerm || 
        cattle.nombre.toLowerCase().includes(this.searchTerm.toLowerCase()) ||
        cattle.identificador.toLowerCase().includes(this.searchTerm.toLowerCase());
      
      return matchesSearch;
    });
  }

  onAddCattle(): void {
    if (!this.newCattle.identificador || !this.newCattle.nombre || !this.newCattle.sexo) {
      this.error = "Complete los campos obligatorios";
      return;
    }

    this.loading = true;
    this.error = "";

    this.cattleService.create(this.newCattle).subscribe({
      next: () => {
        this.showAddForm = false;
        this.newCattle = { identificador: "", nombre: "", sexo: "H" };
        this.loadCattle();
      },
      error: (err) => {
        this.error = err.error?.detail || "Error al crear registro";
        this.loading = false;
      }
    });
  }

  onDelete(id: string): void {
    if (!confirm("¿Está seguro de eliminar este registro?")) {
      return;
    }

    this.cattleService.delete(id).subscribe({
      next: () => {
        this.loadCattle();
      },
      error: (err) => {
        alert("Error al eliminar: " + (err.error?.detail || "Error desconocido"));
      }
    });
  }
}
