import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SongSketchLibraryComponent } from './song-sketch-library.component';

describe('SongSketchLibraryComponent', () => {
  let component: SongSketchLibraryComponent;
  let fixture: ComponentFixture<SongSketchLibraryComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SongSketchLibraryComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(SongSketchLibraryComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
