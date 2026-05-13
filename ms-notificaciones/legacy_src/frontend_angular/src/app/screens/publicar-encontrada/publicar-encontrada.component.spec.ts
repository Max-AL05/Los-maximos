import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PublicarEncontradaComponent } from './publicar-encontrada.component';

describe('PublicarEncontradaComponent', () => {
  let component: PublicarEncontradaComponent;
  let fixture: ComponentFixture<PublicarEncontradaComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [PublicarEncontradaComponent]
    });
    fixture = TestBed.createComponent(PublicarEncontradaComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
