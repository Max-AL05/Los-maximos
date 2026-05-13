// src/app/models/mascota.model.ts
export interface Mascota {
  id: number;
  imagenUrl: string;
  nombre: string;
  descripcion: string;
  estado: 'perdida' | 'encontrada' | 'adopcion';
  // Cualquier otro campo que necesites
}
