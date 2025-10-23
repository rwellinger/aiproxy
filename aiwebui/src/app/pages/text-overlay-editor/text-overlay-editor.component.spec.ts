import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TextOverlayEditorComponent } from './text-overlay-editor.component';

describe('TextOverlayEditorComponent', () => {
  let component: TextOverlayEditorComponent;
  let fixture: ComponentFixture<TextOverlayEditorComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [TextOverlayEditorComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(TextOverlayEditorComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
