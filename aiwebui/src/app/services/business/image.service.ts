import { Injectable } from '@angular/core';
import { StylePreferences, DEFAULT_STYLE_PREFERENCES } from '../../models/image-generation.model';

interface ImageFormData extends Record<string, unknown> {
  prompt?: string;
  size?: string;
}

@Injectable({
  providedIn: 'root',
})
export class ImageService {
  private readonly STORAGE_KEY = 'imageFormData';
  private readonly STYLE_PREFERENCES_KEY = 'imageStylePreferences';

  loadFormData(): ImageFormData {
    const raw = localStorage.getItem(this.STORAGE_KEY);
    return raw ? JSON.parse(raw) : {};
  }

  saveFormData(data: ImageFormData): void {
    localStorage.setItem(this.STORAGE_KEY, JSON.stringify(data));
  }

  clearFormData(): void {
    localStorage.removeItem(this.STORAGE_KEY);
  }

  /**
   * Load style preferences from LocalStorage
   * Returns default values if not found
   */
  loadStylePreferences(): StylePreferences {
    const raw = localStorage.getItem(this.STYLE_PREFERENCES_KEY);
    if (!raw) {
      return { ...DEFAULT_STYLE_PREFERENCES };
    }

    try {
      return JSON.parse(raw);
    } catch {
      return { ...DEFAULT_STYLE_PREFERENCES };
    }
  }

  /**
   * Save style preferences to LocalStorage
   */
  saveStylePreferences(preferences: StylePreferences): void {
    localStorage.setItem(this.STYLE_PREFERENCES_KEY, JSON.stringify(preferences));
  }

  /**
   * Clear style preferences from LocalStorage
   * Returns to default values
   */
  clearStylePreferences(): void {
    localStorage.removeItem(this.STYLE_PREFERENCES_KEY);
  }
}