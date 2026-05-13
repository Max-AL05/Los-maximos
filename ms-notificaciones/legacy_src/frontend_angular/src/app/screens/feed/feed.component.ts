import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { MascotaService } from 'src/services/mascota.service';
import { AuthService } from 'src/services/auth.service';

@Component({
  selector: 'app-feed',
  templateUrl: './feed.component.html',
  styleUrls: ['./feed.component.scss']
})
export class FeedComponent implements OnInit {
  publicaciones: any[] = [];
  filtros = {
    tipo_mascota: '',
    raza: '',
    color: '',
    tamanio: '',
    zona: ''
  };

  modalVisible = false;
  mascotaSeleccionada: any = null;

  constructor(
    private router: Router,
    private mascotaService: MascotaService,
    private authService: AuthService
  ) {}

  ngOnInit(): void {
    this.cargarPublicaciones();
  }

  cargarPublicaciones(): void {
    this.mascotaService.getPublicaciones(this.filtros).subscribe(
      data => this.publicaciones = data,
      error => console.error('Error al cargar publicaciones', error)
    );
  }

  buscar(): void {
    this.cargarPublicaciones();
  }

  limpiarFiltros(): void {
    this.filtros = { tipo_mascota: '', raza: '', color: '', tamanio: '', zona: '' };
    this.cargarPublicaciones();
  }

  cerrarSesion(): void {
    this.authService.logout();
    this.router.navigate(['/home']);
  }

  publicarMascotaPerdida(): void {
    this.router.navigate(['/publicarperdida']);
  }

  publicarMascotaEncontrada(): void {
    this.router.navigate(['/publicarencontrada']);
  }

  publicarEnAdopcion(): void {
    this.router.navigate(['/publicaradopcion']);
  }

  verDetallesMascota(publicacion: any): void {
    this.mascotaSeleccionada = publicacion;
    this.modalVisible = true;
  }

  cerrarModal(): void {
    this.modalVisible = false;
    this.mascotaSeleccionada = null;
  }

  irAlPerfil(): void {
    this.router.navigate(['/perfil']);
  }

  irANotificaciones(): void {
    this.router.navigate(['/notificaciones']);
  }
}
