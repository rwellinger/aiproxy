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

    this.translateService.setDefaultLang('en');
    this.translateService.use(currentLang);
  }

  /**
   * Change the current language
   */
  public changeLanguage(language: Language): void {
    this.translateService.use(language);
    this.settingsService.updateLanguage(language);
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
