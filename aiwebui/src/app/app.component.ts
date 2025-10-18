import { Component, inject, OnInit } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { CommonModule } from '@angular/common';
import { TranslateModule } from '@ngx-translate/core';
import { SideMenuComponent } from './components/side-menu/side-menu.component';
import { AuthService } from './services/business/auth.service';
import { VersionCheckService } from './services/config/version-check.service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, SideMenuComponent, CommonModule, TranslateModule],
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss'
})
export class AppComponent implements OnInit {
  title = 'aiwebui';
  showMobileWarning = false;

  private authService = inject(AuthService);
  private versionCheckService = inject(VersionCheckService);

  public authState$ = this.authService.authState$;

  ngOnInit(): void {
    // Version-Check beim App-Start initialisieren
    this.versionCheckService.initVersionCheck();

    // Check if mobile device (< 768px)
    this.checkMobileDevice();
    window.addEventListener('resize', () => this.checkMobileDevice());
  }

  private checkMobileDevice(): void {
    this.showMobileWarning = window.innerWidth < 768;
  }
}
