import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { HomeComponent } from './screens/home-screen/home-screen.component';
import { LoginComponent } from './screens/login/login.component';
import { RegisterComponent } from './screens/register/register.component';
import { FeedComponent } from './screens/feed/feed.component';
import { ModalMascotaComponent } from './modals/modal-mascota/modal-mascota.component';
import { PublicarMascotaPerdidaComponent } from './screens/publicar-mascota-perdida/publicar-mascota-perdida.component';
import { PublicarEncontradaComponent } from './screens/publicar-encontrada/publicar-encontrada.component';
import { PublicarAdopcionComponent } from './screens/publicar-adopcion/publicar-adopcion.component';
const routes: Routes = [
  { path: 'home', component: HomeComponent },
  { path: 'login', component: LoginComponent },
  { path: 'register', component: RegisterComponent },
  { path: 'feed', component: FeedComponent},
   { path: 'mascota', component: ModalMascotaComponent},
   { path: 'publicarperdida', component: PublicarMascotaPerdidaComponent},
   { path: 'publicarencontrada', component: PublicarEncontradaComponent},
   { path: 'publicaradopcion', component: PublicarAdopcionComponent},
   { path: '', redirectTo: '/home', pathMatch: 'full' }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
