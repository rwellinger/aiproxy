import { Component, OnInit, ViewEncapsulation, inject, HostListener } from '@angular/core';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { TranslateModule, TranslateService } from '@ngx-translate/core';
import { MatCardModule } from '@angular/material/card';
import { MatSnackBarModule } from '@angular/material/snack-bar';
import { firstValueFrom } from 'rxjs';

import { SongService } from '../../services/business/song.service';
import { SketchService } from '../../services/business/sketch.service';
import { NotificationService } from '../../services/ui/notification.service';
import { ChatService } from '../../services/config/chat.service';
import { ProgressService } from '../../services/ui/progress.service';
import { MUSIC_STYLE_CATEGORIES } from '../../models/music-style-chooser.model';

@Component({
  selector: 'app-song-sketch-creator',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatCardModule,
    MatSnackBarModule,
    TranslateModule
  ],
  templateUrl: './song-sketch-creator.component.html',
  styleUrl: './song-sketch-creator.component.scss',
  encapsulation: ViewEncapsulation.None
})
export class SongSketchCreatorComponent implements OnInit {
  sketchForm!: FormGroup;
  isSaving = false;
  isGeneratingTitle = false;
  showTitleDropdown = false;
  selectedTags: string[] = [];

  // Tag categories from shared constants
  tagCategories = MUSIC_STYLE_CATEGORIES;

  private fb = inject(FormBuilder);
  private router = inject(Router);
  private songService = inject(SongService);
  private sketchService = inject(SketchService);
  private notificationService = inject(NotificationService);
  private translate = inject(TranslateService);
  private chatService = inject(ChatService);
  private progressService = inject(ProgressService);

  ngOnInit(): void {
    // Initialize form
    this.sketchForm = this.fb.group({
      title: ['', [Validators.maxLength(500)]],
      lyrics: ['', [Validators.maxLength(10000)]],
      prompt: ['', [Validators.required, Validators.maxLength(1024)]]
    });

    // Load saved form data from sketch-creator context
    const savedData = this.songService.loadFormData('sketch-creator');
    if (savedData && Object.keys(savedData).length > 0) {
      this.sketchForm.patchValue(savedData);

      // Load tags separately (convert string to array)
      if (savedData['tags']) {
        this.selectedTags = this.parseTagsFromString(savedData['tags'] as string);
      }
    }

    // Auto-save form data on changes
    this.sketchForm.valueChanges.subscribe(() => {
      this.saveFormDataWithTags();
    });
  }

  async saveSketch(): Promise<void> {
    if (!this.sketchForm.valid) {
      this.notificationService.error(
        this.translate.instant('songSketch.creator.messages.validationError')
      );
      return;
    }

    const formValue = this.sketchForm.value;
    this.isSaving = true;

    try {
      // Convert selectedTags array to comma-separated string
      const tagsString = this.selectedTags.length > 0
        ? this.selectedTags.join(', ')
        : undefined;

      await firstValueFrom(
        this.sketchService.createSketch({
          title: formValue.title?.trim() || undefined,
          lyrics: formValue.lyrics?.trim() || undefined,
          prompt: formValue.prompt.trim(),
          tags: tagsString,
          workflow: 'draft'
        })
      );

      this.notificationService.success(
        this.translate.instant('songSketch.creator.messages.saved')
      );

      // Reset form and clear saved data
      this.sketchForm.reset();
      this.selectedTags = [];
      this.songService.clearFormData('sketch-creator');

      // Navigate to sketch library after successful save
      this.router.navigate(['/song-sketch-library']);
    } catch (error: any) {
      const errorMessage = error?.error?.detail || error?.message ||
        this.translate.instant('songSketch.creator.messages.error');
      this.notificationService.error(errorMessage);
    } finally {
      this.isSaving = false;
    }
  }

  resetForm(): void {
    this.sketchForm.reset();
    this.selectedTags = [];
    this.songService.clearFormData('sketch-creator');
    this.notificationService.success(
      this.translate.instant('songSketch.creator.messages.resetSuccess')
    );
  }

  navigateToLyricCreator(): void {
    // Save current form state first (including tags)
    this.saveFormDataWithTags();

    // Navigate with context parameter for sketch creator
    this.router.navigate(['/lyriccreation'], {
      queryParams: { context: 'sketch' }
    });
  }

  navigateToMusicStylePrompt(): void {
    // Save current form state first (including tags)
    this.saveFormDataWithTags();

    // Navigate with context parameter for sketch creator
    this.router.navigate(['/music-style-prompt'], {
      queryParams: { context: 'sketch' }
    });
  }

  navigateToSketchLibrary(): void {
    this.router.navigate(['/song-sketch-library']);
  }

  get charCountLyrics(): number {
    return this.sketchForm.get('lyrics')?.value?.length || 0;
  }

  get charCountPrompt(): number {
    return this.sketchForm.get('prompt')?.value?.length || 0;
  }

  // Title generation methods
  toggleTitleDropdown(): void {
    this.showTitleDropdown = !this.showTitleDropdown;
  }

  closeTitleDropdown(): void {
    this.showTitleDropdown = false;
  }

  @HostListener('document:click', ['$event'])
  onDocumentClick(): void {
    this.closeTitleDropdown();
  }

  selectTitleAction(action: 'generate'): void {
    this.closeTitleDropdown();
    if (action === 'generate') {
      this.generateTitle();
    }
  }

  async generateTitle(): Promise<void> {
    let inputText = '';

    // Priority logic: Title > Lyrics > Fallback
    const currentTitle = this.sketchForm.get('title')?.value?.trim();
    const currentLyrics = this.sketchForm.get('lyrics')?.value?.trim();

    if (currentTitle) {
      inputText = currentTitle;
    } else if (currentLyrics) {
      inputText = currentLyrics;
    } else {
      // Fallback constant
      inputText = this.translate.instant('songSketch.creator.messages.generateTitleFallback');
    }

    this.isGeneratingTitle = true;
    try {
      const generatedTitle = await this.progressService.executeWithProgress(
        () => this.chatService.generateTitle(inputText),
        this.translate.instant('songSketch.creator.messages.generatingTitle'),
        this.translate.instant('songSketch.creator.messages.generatingTitleHint')
      );
      this.sketchForm.patchValue({ title: this.removeQuotes(generatedTitle as string) });
    } catch (error: any) {
      this.notificationService.error(
        this.translate.instant('songSketch.creator.messages.titleGenerationError') + ': ' + error.message
      );
    } finally {
      this.isGeneratingTitle = false;
    }
  }

  private removeQuotes(text: string): string {
    return text.replace(/^["']|["']$/g, '').trim();
  }

  // Tag management methods
  toggleTag(tag: string): void {
    const index = this.selectedTags.indexOf(tag);
    if (index > -1) {
      this.selectedTags.splice(index, 1);
    } else {
      this.selectedTags.push(tag);
    }
    // Auto-save when tags change
    this.saveFormDataWithTags();
  }

  isTagSelected(tag: string): boolean {
    return this.selectedTags.includes(tag);
  }

  private parseTagsFromString(tagsString: string): string[] {
    if (!tagsString || !tagsString.trim()) {
      return [];
    }
    return tagsString.split(',')
      .map(tag => tag.trim())
      .filter(tag => tag.length > 0);
  }

  private saveFormDataWithTags(): void {
    const formValue = this.sketchForm.value;
    const tagsString = this.selectedTags.length > 0
      ? this.selectedTags.join(', ')
      : '';

    this.songService.saveFormData({
      ...formValue,
      tags: tagsString
    }, 'sketch-creator');
  }
}
