import {ComponentFixture, TestBed} from "@angular/core/testing";
import {provideHttpClient} from "@angular/common/http";
import {provideHttpClientTesting} from "@angular/common/http/testing";
import {TranslateModule} from "@ngx-translate/core";

import {SongViewComponent} from "./song-view.component";

describe("SongViewComponent", () => {
    let component: SongViewComponent;
    let fixture: ComponentFixture<SongViewComponent>;

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            imports: [SongViewComponent,
                TranslateModule.forRoot()
            ],
            providers: [
                provideHttpClient(),
                provideHttpClientTesting()
            ]
        })
            .compileComponents();

        fixture = TestBed.createComponent(SongViewComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it("should create", () => {
        expect(component).toBeTruthy();
    });
});
