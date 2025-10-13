export type Language = 'en' | 'de';

export interface UserSettings {
  songListLimit: number;
  imageListLimit: number;
  language: Language;
}

export const DEFAULT_USER_SETTINGS: UserSettings = {
  songListLimit: 10,
  imageListLimit: 10,
  language: 'en'
};