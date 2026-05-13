import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PublicarMascotaPerdidaComponent } from './publicar-mascota-perdida.component';

describe('PublicarMascotaPerdidaComponent', () => {
  let component: PublicarMascotaPerdidaComponent;
  let fixture: ComponentFixture<PublicarMascotaPerdidaComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [PublicarMascotaPerdidaComponent]
    });
    fixture = TestBed.createComponent(PublicarMascotaPerdidaComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
