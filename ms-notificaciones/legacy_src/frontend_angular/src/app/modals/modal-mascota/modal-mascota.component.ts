import { Component, ElementRef, Input, OnInit, Output, EventEmitter } from '@angular/core';

@Component({
  selector: 'app-modal-mascota',
  templateUrl: './modal-mascota.component.html',
  styleUrls: ['./modal-mascota.component.scss']
})
export class ModalMascotaComponent implements OnInit {
  @Input() mascota: any = null;
  @Output() cerrar = new EventEmitter<void>();

  // Variables para almacenar la información de la mascota
  nombreMascota: string = '';
  estado: string = '';
  descripcion: string = '';
  imagenUrl: string = '';
  detalles: any = {};

  // Helper para iterar sobre las propiedades de un objeto en el template
  objectKeys = Object.keys;

  constructor(private el: ElementRef) { }

  ngOnInit(): void {
    // Añadir class al body para prevenir scroll
    document.body.classList.add('modal-abierto');

    // Event listener para cerrar con escape
    document.addEventListener('keydown', this.handleEscapeKey);

    // Procesar los datos de la mascota dependiendo del tipo de publicación
    this.procesarDatosMascota();
  }

  procesarDatosMascota(): void {
    if (!this.mascota) return;

    // Determinar el tipo de publicación y extraer datos relevantes
    if (this.mascota.mascotas && this.mascota.mascotas.length > 0) {
      // Mascota perdida
      const mascotaData = this.mascota.mascotas[0];
      this.nombreMascota = mascotaData.nombre || 'Sin nombre';
      this.estado = 'perdida';
      this.descripcion = this.mascota.contenido || '';
      this.imagenUrl = mascotaData.fotos ? 'http://localhost:8000' + mascotaData.fotos : 'assets/images/default-pet.jpg';
      this.detalles = {
        tipo: mascotaData.tipo_mascota || 'No especificado',
        raza: mascotaData.raza || 'No especificada',
        color: mascotaData.color || 'No especificado',
        tamanio: mascotaData.tamanio || 'No especificado',
        zona: this.mascota.zona || 'No especificada',
        fecha: this.mascota.fecha_creacion || 'No especificada'
      };
    } else if (this.mascota.mascotas_encontradas && this.mascota.mascotas_encontradas.length > 0) {
      // Mascota encontrada
      const mascotaData = this.mascota.mascotas_encontradas[0];
      this.nombreMascota = mascotaData.nombre || 'Sin nombre';
      this.estado = 'encontrada';
      this.descripcion = this.mascota.contenido || '';
      this.imagenUrl = mascotaData.fotos ? 'http://localhost:8000' + mascotaData.fotos : 'assets/images/default-pet.jpg';
      this.detalles = {
        tipo: mascotaData.tipo_mascota || 'No especificado',
        raza: mascotaData.raza || 'No especificada',
        color: mascotaData.color || 'No especificado',
        tamanio: mascotaData.tamanio || 'No especificado',
        zona: this.mascota.zona || 'No especificada',
        fecha: this.mascota.fecha_creacion || 'No especificada'
      };
    } else if (this.mascota.mascotas_adopcion && this.mascota.mascotas_adopcion.length > 0) {
      // Mascota en adopción
      const mascotaData = this.mascota.mascotas_adopcion[0];
      this.nombreMascota = mascotaData.nombre || 'Sin nombre';
      this.estado = 'adopcion';
      this.descripcion = this.mascota.contenido || '';
      this.imagenUrl = mascotaData.foto ? 'http://localhost:8000' + mascotaData.foto : 'assets/images/default-pet.jpg';
      this.detalles = {
        tipo: mascotaData.tipo_mascota || 'No especificado',
        raza: mascotaData.raza || 'No especificada',
        color: mascotaData.color || 'No especificado',
        tamanio: mascotaData.tamanio || 'No especificado',
        edad: mascotaData.edad || 'No especificada',
        sexo: mascotaData.sexo || 'No especificado',
        fecha: this.mascota.fecha_creacion || 'No especificada'
      };
    } else {
      // Caso por defecto si no se encuentra información
      this.nombreMascota = 'Mascota';
      this.estado = this.mascota.tipo || 'desconocido';
      this.descripcion = this.mascota.contenido || 'Sin descripción disponible';
      this.imagenUrl = 'assets/images/default-pet.jpg';
    }
  }

  ngOnDestroy(): void {
    // Eliminar class del body al destruir el componente
    document.body.classList.remove('modal-abierto');

    // Eliminar event listener
    document.removeEventListener('keydown', this.handleEscapeKey);
  }

  handleEscapeKey = (event: KeyboardEvent) => {
    if (event.key === 'Escape') {
      this.cerrarModal();
    }
  }

  cerrarModal(): void {
    this.cerrar.emit();
  }

  // Cerrar si se hace clic fuera del contenido del modal
  onBackdropClick(event: MouseEvent): void {
    if (event.target === this.el.nativeElement.querySelector('.modal-backdrop')) {
      this.cerrarModal();
    }
  }
}
