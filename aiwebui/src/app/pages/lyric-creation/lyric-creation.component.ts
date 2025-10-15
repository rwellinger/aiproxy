import {Component, OnInit, ViewEncapsulation, inject} from '@angular/core';
import {FormBuilder, FormGroup, ReactiveFormsModule} from '@angular/forms';
import {CommonModule} from '@angular/common';
import {MatDialog} from '@angular/material/dialog';
import {TranslateModule, TranslateService} from '@ngx-translate/core';
import {SongService} from '../../services/business/song.service';
import {NotificationService} from '../../services/ui/notification.service';
import {ChatService} from '../../services/config/chat.service';
import {MatSnackBarModule} from '@angular/material/snack-bar';
import {MatCardModule} from '@angular/material/card';
import {ProgressService} from '../../services/ui/progress.service';
import {LyricArchitectModalComponent} from '../../components/lyric-architect-modal/lyric-architect-modal.component';
import {LyricArchitectureService} from '../../services/lyric-architecture.service';

@Component({
    selector: 'app-lyric-creation',
    standalone: true,
    imports: [CommonModule, ReactiveFormsModule, MatSnackBarModule, MatCardModule, TranslateModule],
    templateUrl: './lyric-creation.component.html',
    styleUrl: './lyric-creation.component.scss',
    encapsulation: ViewEncapsulation.None
})
export class LyricCreationComponent implements OnInit {
    lyricForm!: FormGroup;
    isGeneratingLyrics = false;
    isTranslatingLyrics = false;

    private fb = inject(FormBuilder);
    private songService = inject(SongService);
    private notificationService = inject(NotificationService);
    private chatService = inject(ChatService);
    private progressService = inject(ProgressService);
    private dialog = inject(MatDialog);
    private architectureService = inject(LyricArchitectureService);
    private translate = inject(TranslateService);

    ngOnInit() {
        this.lyricForm = this.fb.group({
            lyrics: ['']
        });

        // Load saved lyrics from song generator storage
        const savedData = this.songService.loadFormData();
        if (savedData.lyrics) {
            this.lyricForm.patchValue({lyrics: savedData.lyrics});
        }

        // Auto-save lyrics on changes
        this.lyricForm.valueChanges.subscribe(value => {
            this.saveLyrics(value.lyrics);
        });
    }

    private saveLyrics(lyrics: string): void {
        // Load existing song generator data and update only lyrics
        const existingData = this.songService.loadFormData();
        this.songService.saveFormData({
            ...existingData,
            lyrics: lyrics
        });
    }

    clearLyrics(): void {
        this.lyricForm.patchValue({lyrics: ''});
        this.notificationService.success(this.translate.instant('lyricCreation.autoSaved'));
    }

    async generateLyrics() {
        const currentText = this.lyricForm.get('lyrics')?.value?.trim();
        if (!currentText) {
            this.notificationService.error(this.translate.instant('lyricCreation.errors.textRequired'));
            return;
        }

        this.isGeneratingLyrics = true;
        try {
            const generatedLyrics = await this.progressService.executeWithProgress(
                () => this.chatService.generateLyrics(currentText),
                this.translate.instant('songGenerator.progress.generatingLyrics'),
                this.translate.instant('songGenerator.progress.generatingLyricsHint')
            );
            this.lyricForm.patchValue({lyrics: this.removeQuotes(generatedLyrics)});
        } catch (error: any) {
            this.notificationService.error(`Error generating lyrics: ${error.message}`);
        } finally {
            this.isGeneratingLyrics = false;
        }
    }

    async translateLyrics() {
        const currentLyrics = this.lyricForm.get('lyrics')?.value?.trim();
        if (!currentLyrics) {
            this.notificationService.error(this.translate.instant('lyricCreation.errors.lyricsRequired'));
            return;
        }

        this.isTranslatingLyrics = true;
        try {
            const translatedLyrics = await this.progressService.executeWithProgress(
                () => this.chatService.translateLyric(currentLyrics),
                this.translate.instant('songGenerator.progress.translatingLyrics'),
                this.translate.instant('songGenerator.progress.translatingLyricsHint')
            );
            this.lyricForm.patchValue({lyrics: this.removeQuotes(translatedLyrics)});
        } catch (error: any) {
            this.notificationService.error(`Error translating lyrics: ${error.message}`);
        } finally {
            this.isTranslatingLyrics = false;
        }
    }

    openLyricArchitectModal(): void {
        const dialogRef = this.dialog.open(LyricArchitectModalComponent, {
            width: '800px',
            maxWidth: '90vw',
            maxHeight: '90vh',
            disableClose: false,
            autoFocus: true
        });

        dialogRef.afterClosed().subscribe(result => {
            if (result && result.architectureString) {
                this.notificationService.success(this.translate.instant('songGenerator.success.architectureUpdated'));
            }
        });
    }

    private removeQuotes(text: string): string {
        if (!text) return text;
        return text.replace(/^["']|["']$/g, '').trim();
    }

    get characterCount(): number {
        return this.lyricForm.get('lyrics')?.value?.length || 0;
    }
}
