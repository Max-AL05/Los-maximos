import { Component, OnInit, ViewChild, ElementRef } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { MascotaService } from 'src/services/mascota.service';
import { AuthService } from 'src/services/auth.service';

@Component({
  selector: 'app-publicar-encontrada',
  templateUrl: './publicar-encontrada.component.html',
  styleUrls: ['./publicar-encontrada.component.scss']
})
export class PublicarEncontradaComponent implements OnInit {
  mascotaForm: FormGroup;
  fotoPreviewUrl: string | null = null;
  fotoSeleccionada: File | null = null;
  token: string | null = null;
  loading = false;
  submitted = false;

  @ViewChild('fileInput') fileInput!: ElementRef;

  constructor(
    private formBuilder: FormBuilder,
    private router: Router,
    private mascotaService: MascotaService,
    private authService: AuthService
  ) {
    this.mascotaForm = this.formBuilder.group({
      nombre: ['', Validators.required],
      especie: ['', Validators.required],
      otra_especie: [''],
      sexo: ['', Validators.required],
      tamaño: ['', Validators.required],
      color: ['', Validators.required],
      senas_particulares: ['', [Validators.required, Validators.minLength(10), Validators.maxLength(300)]],
      ultima_ubicacion: ['', Validators.required],
      fecha_encontrada: ['', Validators.required],
      contacto: ['', [Validators.required, Validators.pattern('^[0-9]{3}-[0-9]{3}-[0-9]{4}$|^[0-9]{10}$')]],
      foto: [null, Validators.required]
    });

    this.token = localStorage.getItem('token');
  }

  ngOnInit(): void {
    const fechaActual = new Date().toISOString().split('T')[0];
    this.mascotaForm.patchValue({
      fecha_encontrada: fechaActual
    });

    this.mascotaForm.get('especie')?.valueChanges.subscribe(especie => {
      const otraEspecieControl = this.mascotaForm.get('otra_especie');
      if (especie === 'otro') {
        otraEspecieControl?.setValidators([Validators.required]);
      } else {
        otraEspecieControl?.clearValidators();
      }
      otraEspecieControl?.updateValueAndValidity();
    });
  }

  onFileChange(event: any): void {
    if (event.target.files && event.target.files.length) {
      const file = event.target.files[0];
      this.fotoSeleccionada = file;
      this.mascotaForm.patchValue({
        foto: file
      });
      // Previsualización
      const reader = new FileReader();
      reader.onload = (e: any) => {
        this.fotoPreviewUrl = e.target.result;
      };
      reader.readAsDataURL(file);
    }
  }

  eliminarImagen(event: Event): void {
    event.stopPropagation();
    this.fotoSeleccionada = null;
    this.fotoPreviewUrl = null;
    this.mascotaForm.patchValue({ foto: null });
    this.fileInput.nativeElement.value = '';
  }

  onSubmit(): void {
    this.submitted = true;

    if (this.mascotaForm.invalid) {
      this.marcarCamposComoTocados(this.mascotaForm);
      const firstElementWithError = document.querySelector('.ng-invalid.ng-touched');
      if (firstElementWithError) {
        firstElementWithError.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
      return;
    }

    this.loading = true;

    if (this.token) {
      const formData = new FormData();
      Object.entries(this.mascotaForm.value).forEach(([key, value]) => {
        if (value !== null && value !== undefined && key !== 'foto') {
          formData.append(key, value as string);
        }
      });

      formData.append('estado_publicacion', 'encontrado');

      if (this.fotoSeleccionada) {
        formData.append('fotos', this.fotoSeleccionada);
      }

      this.mascotaService.publicarMascotaEncontrada(formData, this.token).subscribe(
        data => {
          this.loading = false;
          alert('¡Mascota encontrada publicada con éxito!');
          this.router.navigate(['/feed']);
        },
        error => {
          this.loading = false;
          console.error('Error al publicar la mascota encontrada', error);
        }
      );
    } else {
      console.error('No se encontró un token JWT válido.');
      this.loading = false;
    }
  }

  marcarCamposComoTocados(formGroup: FormGroup): void {
    Object.keys(formGroup.controls).forEach(campo => {
      const control = formGroup.get(campo);
      control?.markAsTouched();
      if (control instanceof FormGroup) {
        this.marcarCamposComoTocados(control);
      }
    });
  }

  cancelar(): void {
    if (confirm('¿Estás seguro de que deseas cancelar? Se perderán los datos ingresados.')) {
      this.router.navigate(['/feed']);
    }
  }
}
