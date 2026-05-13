import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { ReactiveFormsModule } from '@angular/forms';
import { HttpClientModule } from '@angular/common/http'; // Añadido para soportar HttpClient
import { FormsModule } from '@angular/forms';
import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { HomeComponent } from './screens/home-screen/home-screen.component';
import { LoginComponent } from './screens/login/login.component';
import { RegisterComponent } from './screens/register/register.component';
import { FeedComponent } from './screens/feed/feed.component';
import { ModalMascotaComponent } from './modals/modal-mascota/modal-mascota.component';
import { PublicarMascotaPerdidaComponent } from './screens/publicar-mascota-perdida/publicar-mascota-perdida.component';
import { PublicarEncontradaComponent } from './screens/publicar-encontrada/publicar-encontrada.component';
import { PublicarAdopcionComponent } from './screens/publicar-adopcion/publicar-adopcion.component';

@NgModule({
  declarations: [
    AppComponent,
    HomeComponent,
    LoginComponent,
    RegisterComponent,
    FeedComponent,
    ModalMascotaComponent,
    PublicarMascotaPerdidaComponent,
    PublicarEncontradaComponent,
    PublicarAdopcionComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    ReactiveFormsModule,
    HttpClientModule, // Añadido para habilitar HttpClient
    FormsModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
