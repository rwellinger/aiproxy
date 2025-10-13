import { Injectable, inject } from '@angular/core';
import { TranslateService } from '@ngx-translate/core';
import { UserSettingsService } from './user-settings.service';
import { Language } from '../models/user-settings.model';

@Injectable({
  providedIn: 'root'
})
export class LanguageService {
  private translateService = inject(TranslateService);
  private settingsService = inject(UserSettingsService);

  constructor() {
    this.initializeLanguage();
  }

  /**
   * Initialize language from user settings
   */
  private initializeLanguage(): void {
    const settings = this.settingsService.getCurrentSettings();
    const currentLang = settings.language || 'en';

    // Default language is already set in app.config.ts
    // Subscribe to use() to ensure translation loading completes
    this.translateService.use(currentLang).subscribe({
      error: (error) => console.error('Error loading translations:', error)
    });
  }

  /**
   * Change the current language
   */
  public changeLanguage(language: Language): void {
    this.translateService.use(language).subscribe({
      next: () => this.settingsService.updateLanguage(language),
      error: (error) => console.error('Error changing language:', error)
    });
  }

  /**
   * Get the current language
   */
  public getCurrentLanguage(): Language {
    return this.settingsService.getCurrentSettings().language;
  }

  /**
   * Get available languages
   */
  public getAvailableLanguages(): {code: Language, name: string}[] {
    return [
      { code: 'en', name: 'English' },
      { code: 'de', name: 'Deutsch' }
    ];
  }
}
