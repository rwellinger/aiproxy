import { ComponentFixture, TestBed } from '@angular/core/testing';

import { GridPositionSelectorComponent } from './grid-position-selector.component';

describe('GridPositionSelectorComponent', () => {
  let component: GridPositionSelectorComponent;
  let fixture: ComponentFixture<GridPositionSelectorComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [GridPositionSelectorComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(GridPositionSelectorComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
