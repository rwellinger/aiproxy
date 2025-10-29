export type Language = 'en' | 'de';

export interface UserSettings {
  songListLimit: number;
  imageListLimit: number;
  promptListLimit: number;
  sketchListLimit: number;
  equipmentListLimit: number;
  language: Language;
}

export const DEFAULT_USER_SETTINGS: UserSettings = {
  songListLimit: 8,
  imageListLimit: 8,
  promptListLimit: 8,
  sketchListLimit: 8,
  equipmentListLimit: 7,
  language: 'en'
};