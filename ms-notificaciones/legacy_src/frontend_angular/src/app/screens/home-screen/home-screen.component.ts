import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';

@Component({
  selector: 'app-home',
  templateUrl: './home-screen.component.html',
  styleUrls: ['./home-screen.component.scss']
})
export class HomeComponent implements OnInit {

  constructor(private router: Router) { }

  ngOnInit(): void {
    // Inicialización del componente si es necesario
  }

  /**
   * Navega a la página de inicio de sesión
   */
  navigateToLogin(): void {

    console.log('Navegando a login...');
    this.router.navigate(['/login']);
  }

  /**
   * Navega a la página de registro
   */
  navigateToRegister(): void {

    console.log('Navegando a registro...');
    this.router.navigate(['/register']);
  }
}
