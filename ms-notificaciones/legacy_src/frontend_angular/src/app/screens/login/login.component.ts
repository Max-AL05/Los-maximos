import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from 'src/services/auth.service';  // Inyecta el servicio de autenticación
import { Injectable } from '@angular/core';
@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.scss']
})
export class LoginComponent implements OnInit {
  loginForm!: FormGroup;
  submitted = false;
  showPassword = false;

  constructor(
    private formBuilder: FormBuilder,
    private router: Router,
    private authService: AuthService  // Inyecta el servicio
  ) { }

  ngOnInit(): void {
    this.initForm();
  }

  initForm(): void {
    this.loginForm = this.formBuilder.group({
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required, Validators.minLength(6)]],
      remember: [false] // Añadido como un control booleano
    });
  }

  get f() {
    return this.loginForm.controls;
  }

  togglePasswordVisibility(): void {
    this.showPassword = !this.showPassword;
  }

  onSubmit(): void {
    this.submitted = true;
    if (this.loginForm.invalid) {
      return;
    }

    const { email, password } = this.loginForm.value;

    this.authService.login(email, password).subscribe(
      data => {
        // Si el login es exitoso, almacenar el token en localStorage
        localStorage.setItem('token', data.token);
        // Redirigir a la página de feed
        this.router.navigate(['/feed']);
      },
      error => {
        // Manejar errores de autenticación
        console.error('Login error:', error);
      }
    );
  }
}
