import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting } from '@angular/common/http/testing';
import { TranslateModule } from '@ngx-translate/core';

import { SongProfileComponent } from './song-profile.component';

describe('SongProfileComponent', () => {
  let component: SongProfileComponent;
  let fixture: ComponentFixture<SongProfileComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SongProfileComponent,
        TranslateModule.forRoot()
      ],
      providers: [
        provideHttpClient(),
        provideHttpClientTesting()
      ]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(SongProfileComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
