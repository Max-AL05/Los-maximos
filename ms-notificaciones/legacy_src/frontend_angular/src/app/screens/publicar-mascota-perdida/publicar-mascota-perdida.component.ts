import { Component, OnInit, ViewChild, ElementRef } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { MascotaService } from 'src/services/mascota.service';
import { AuthService } from 'src/services/auth.service';

@Component({
  selector: 'app-publicar-mascota-perdida',
  templateUrl: './publicar-mascota-perdida.component.html',
  styleUrls: ['./publicar-mascota-perdida.component.scss']
})
export class PublicarMascotaPerdidaComponent implements OnInit {
  formularioMascota: FormGroup;
  imagenPreview: string | null = null;
  imagenFile: File | null = null;
  token: string | null = null;

  @ViewChild('fileInput') fileInput!: ElementRef;

  constructor(
    private fb: FormBuilder,
    private router: Router,
    private mascotaService: MascotaService,
    private authService: AuthService
  ) {
    this.formularioMascota = this.fb.group({
      nombre: ['', Validators.required],
      especie: ['', Validators.required],
      otra_especie: [''],
      raza: [''],
      edad: [''],
      unidad_edad: ['año(s)'],
      sexo: [''],
      color_principal: [''],
      caracteristicas_especiales: [''],
      fecha_perdida: ['', Validators.required],
      lugar_perdida: ['', Validators.required],
      ultima_vez: [''],
      telefono: ['', [Validators.required, Validators.pattern('^[0-9]{3}-[0-9]{3}-[0-9]{4}$|^[0-9]{10}$')]],
      notas_adicionales: ['']
    });

    this.token = localStorage.getItem('token');
  }

  ngOnInit(): void {
    this.formularioMascota.get('especie')?.valueChanges.subscribe(especie => {
      const otraEspecieControl = this.formularioMascota.get('otra_especie');
      if (especie === 'otro') {
        otraEspecieControl?.setValidators([Validators.required]);
      } else {
        otraEspecieControl?.clearValidators();
      }
      otraEspecieControl?.updateValueAndValidity();
    });
  }

  onSubmit(): void {
    if (this.formularioMascota.valid) {
      const formData = new FormData();
      Object.entries(this.formularioMascota.value).forEach(([key, value]) => {
        if (value !== null && value !== undefined) {
          formData.append(key, value as string);
        }
      });

      if (this.imagenFile) {
        formData.append('fotos', this.imagenFile);
      }
      if (this.token) {
        this.mascotaService.publicarMascotaPerdida(formData, this.token).subscribe(
          data => {
            alert('¡Mascota perdida publicada con éxito!');
            this.volver();
          },
          error => {
            console.error('Error al publicar la mascota perdida', error);
          }
        );
      } else {
        console.error('No se encontró un token JWT válido.');
      }
    } else {
      this.marcarCamposComoTocados(this.formularioMascota);
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

  triggerFileInput(): void {
    this.fileInput.nativeElement.click();
  }

  onImageSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files.length > 0) {
      const file = input.files[0];
      this.imagenFile = file;
      const reader = new FileReader();
      reader.onload = () => {
        this.imagenPreview = reader.result as string;
      };
      reader.readAsDataURL(file);
    }
  }

  eliminarImagen(event: Event): void {
    event.stopPropagation();
    this.imagenPreview = null;
    this.imagenFile = null;
    this.fileInput.nativeElement.value = '';
  }

  volver(): void {
    this.router.navigate(['/feed']);
  }
}
