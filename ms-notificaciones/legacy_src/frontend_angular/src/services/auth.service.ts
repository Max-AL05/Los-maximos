import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private apiUrl = 'http://localhost:8000/api';  // Cambia esto a la URL de tu backend

  constructor(private http: HttpClient) {}

  // Login
  login(email: string, password: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/login/`, { email, password });
  }

  // Registro
  register(firstName: string, lastName: string, email: string, phone: string, password: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/register/`, { firstName, lastName, email, phone, password });
  }

  logout(): void {
    localStorage.removeItem('token');
    // ...otros datos si es necesario
  }
}
