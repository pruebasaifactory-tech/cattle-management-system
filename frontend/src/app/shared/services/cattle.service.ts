import { Injectable } from "@angular/core";
import { HttpClient, HttpParams } from "@angular/common/http";
import { Observable } from "rxjs";
import { environment } from "../../../environments/environment";

export interface Cattle {
  id: string;
  identificador: string;
  nombre: string;
  raza: string | null;
  fecha_nacimiento: string | null;
  sexo: string;
  estado: string;
  peso_actual: number | null;
}

export interface CattleCreate {
  identificador: string;
  nombre: string;
  raza?: string;
  fecha_nacimiento?: string;
  sexo: string;
  peso_actual?: number;
}

@Injectable({
  providedIn: "root"
})
export class CattleService {
  private apiUrl = `${environment.apiUrl}/cattle`;

  constructor(private http: HttpClient) {}

  getAll(estado?: string): Observable<Cattle[]> {
    let params = new HttpParams();
    if (estado) {
      params = params.set("estado", estado);
    }
    return this.http.get<Cattle[]>(this.apiUrl, { params });
  }

  getById(id: string): Observable<Cattle> {
    return this.http.get<Cattle>(`${this.apiUrl}/${id}`);
  }

  create(cattle: CattleCreate): Observable<Cattle> {
    return this.http.post<Cattle>(this.apiUrl, cattle);
  }

  update(id: string, cattle: Partial<Cattle>): Observable<Cattle> {
    return this.http.put<Cattle>(`${this.apiUrl}/${id}`, cattle);
  }

  delete(id: string): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/${id}`);
  }
}
