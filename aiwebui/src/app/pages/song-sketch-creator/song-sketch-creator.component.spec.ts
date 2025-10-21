import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SongSketchCreatorComponent } from './song-sketch-creator.component';

describe('SongSketchCreatorComponent', () => {
  let component: SongSketchCreatorComponent;
  let fixture: ComponentFixture<SongSketchCreatorComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SongSketchCreatorComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(SongSketchCreatorComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
