import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { MascotaService } from 'src/services/mascota.service';

@Component({
  selector: 'app-publicar-adopcion',
  templateUrl: './publicar-adopcion.component.html',
  styleUrls: ['./publicar-adopcion.component.scss']
})
export class PublicarAdopcionComponent implements OnInit {
  adopcionForm: FormGroup;
  imagenSeleccionada: string | ArrayBuffer | null = null;
  imagenFile: File | null = null;
  enviando: boolean = false;
  enviado: boolean = false;
  error: string | null = null;
  token: string | null = null;

  especies: string[] = ['Perro', 'Gato', 'Ave', 'Conejo', 'Hámster', 'Otro'];
  edades: string[] = ['Cachorro (0-1 año)', 'Joven (1-3 años)', 'Adulto (3-8 años)', 'Senior (8+ años)'];
  tamanios: string[] = ['Pequeño', 'Mediano', 'Grande', 'Muy grande'];
  sexos: string[] = ['Macho', 'Hembra', 'Desconocido'];

  constructor(
    private fb: FormBuilder,
    private router: Router,
    private mascotaService: MascotaService
  ) {
    this.adopcionForm = this.fb.group({
      nombre: ['', [Validators.required, Validators.maxLength(50)]],
      especie: ['', Validators.required],
      raza: ['', Validators.maxLength(50)],
      edad: ['', Validators.required],
      tamanio: ['', Validators.required],
      sexo: ['', Validators.required],
      descripcion: ['', [Validators.required, Validators.minLength(20), Validators.maxLength(500)]],
      ubicacion: ['', [Validators.required, Validators.maxLength(100)]],
      vacunado: [false],
      esterilizado: [false],
      amigableConMascotas: [false],
      amigableConNinos: [false],
      necesidadesEspeciales: ['', Validators.maxLength(200)],
      contactoNombre: ['', [Validators.required, Validators.maxLength(100)]],
      contactoEmail: ['', [Validators.required, Validators.email]],
      contactoTelefono: ['', [Validators.required, Validators.pattern('^[0-9]{10}$')]]
    });
    this.token = localStorage.getItem('token'); // Se obtiene el token al crear el componente
  }

  ngOnInit(): void {
    window.scrollTo(0, 0);
  }

  onImagenSeleccionada(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files[0]) {
      const archivo = input.files[0];

      // Validar tamaño (máximo 5MB)
      if (archivo.size > 5 * 1024 * 1024) {
        this.error = 'La imagen no debe exceder 5MB';
        this.imagenSeleccionada = null;
        this.imagenFile = null;
        input.value = '';
        return;
      }

      // Validar tipo
      if (!archivo.type.match('image.*')) {
        this.error = 'El archivo debe ser una imagen (formatos permitidos: JPG, PNG, JPEG, GIF)';
        this.imagenSeleccionada = null;
        this.imagenFile = null;
        input.value = '';
        return;
      }

      const reader = new FileReader();
      reader.onload = () => {
        this.imagenSeleccionada = reader.result;
        this.imagenFile = archivo;
        this.error = null;
      };
      reader.readAsDataURL(archivo);
    }
  }

  eliminarImagen(): void {
    this.imagenSeleccionada = null;
    this.imagenFile = null;
    this.error = null;
  }

  onSubmit(): void {
    if (this.adopcionForm.invalid || !this.imagenFile || this.error) {
      this.adopcionForm.markAllAsTouched();
      if (!this.imagenFile) {
        this.error = 'La imagen es obligatoria';
      }
      return;
    }

    this.enviando = true;

    const formData = new FormData();
    Object.entries(this.adopcionForm.value).forEach(([key, value]) => {
      formData.append(`mascota_adopcion.${key}`, value as string);
    });
    if (this.imagenFile) {
      formData.append('mascota_adopcion.foto', this.imagenFile);
    }

    // Obtener el token actualizado antes de enviar
    this.token = localStorage.getItem('token');
    if (this.token) {
      this.mascotaService.registrarAdopcion(formData, this.token).subscribe(
        response => {
          this.enviando = false;
          this.enviado = true;
          setTimeout(() => {
            this.router.navigate(['/feed']);
          }, 2000);
        },
        error => {
          this.enviando = false;
          this.error = 'Error al registrar la adopción';
        }
      );
    } else {
      this.enviando = false;
      this.error = 'Debes iniciar sesión para publicar una adopción.';
    }
  }

  cancelar(): void {
    this.router.navigate(['/feed']);
  }

  campoNoValido(campo: string): boolean {
    return this.adopcionForm.get(campo)?.invalid && this.adopcionForm.get(campo)?.touched || false;
  }

  getMensajeError(campo: string): string {
    const control = this.adopcionForm.get(campo);

    if (control?.hasError('required')) {
      return 'Este campo es obligatorio';
    }

    if (control?.hasError('email')) {
      return 'Ingrese un correo electrónico válido';
    }

    if (control?.hasError('pattern')) {
      if (campo === 'contactoTelefono') {
        return 'Ingrese un número de teléfono válido de 10 dígitos';
      }
      return 'Formato inválido';
    }

    if (control?.hasError('minlength')) {
      const minLength = control.errors?.['minlength'].requiredLength;
      return `Debe tener al menos ${minLength} caracteres`;
    }

    if (control?.hasError('maxlength')) {
      const maxLength = control.errors?.['maxlength'].requiredLength;
      return `No debe exceder ${maxLength} caracteres`;
    }

    return 'Campo inválido';
  }
}
