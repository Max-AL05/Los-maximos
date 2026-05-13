import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PublicarAdopcionComponent } from './publicar-adopcion.component';

describe('PublicarAdopcionComponent', () => {
  let component: PublicarAdopcionComponent;
  let fixture: ComponentFixture<PublicarAdopcionComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [PublicarAdopcionComponent]
    });
    fixture = TestBed.createComponent(PublicarAdopcionComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
