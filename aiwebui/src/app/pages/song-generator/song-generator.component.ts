import {Component, OnInit, ViewEncapsulation, inject, HostListener, ViewChild, ElementRef} from '@angular/core';
import {FormBuilder, FormGroup, ReactiveFormsModule, Validators} from '@angular/forms';
import {CommonModule} from '@angular/common';
import {MatDialog} from '@angular/material/dialog';
import {TranslateModule, TranslateService} from '@ngx-translate/core';
import {SongService} from '../../services/business/song.service';
import {ApiConfigService} from '../../services/config/api-config.service';
import {NotificationService} from '../../services/ui/notification.service';
import {ChatService} from '../../services/config/chat.service';
import {MatSnackBarModule} from '@angular/material/snack-bar';
import {MatCardModule} from '@angular/material/card';
import {SongDetailPanelComponent} from '../../components/song-detail-panel/song-detail-panel.component';
import {ProgressService} from '../../services/ui/progress.service';
import {LyricArchitectModalComponent} from '../../components/lyric-architect-modal/lyric-architect-modal.component';
import {LyricArchitectureService} from '../../services/lyric-architecture.service';
import {MusicStyleChooserModalComponent} from '../../components/music-style-chooser-modal/music-style-chooser-modal.component';
import {MusicStyleChooserService} from '../../services/music-style-chooser.service';

@Component({
    selector: 'app-song-generator',
    standalone: true,
    imports: [CommonModule, ReactiveFormsModule, MatSnackBarModule, MatCardModule, SongDetailPanelComponent, TranslateModule],
    templateUrl: './song-generator.component.html',
    styleUrl: './song-generator.component.scss',
    encapsulation: ViewEncapsulation.None
})
export class SongGeneratorComponent implements OnInit {
    songForm!: FormGroup;
    isLoading = false;
    isImprovingPrompt = false;
    isTranslatingLyrics = false;
    isGeneratingLyrics = false;
    isTranslatingStylePrompt = false;
    isGeneratingTitle = false;
    showLyricsDropdown = false;
    showStyleDropdown = false;
    showTitleDropdown = false;
    loadingMessage = '';
    result = '';
    currentlyPlaying: string | null = null;
    currentSongId: string | null = null;
    isInstrumentalMode = false; // Computed property to avoid method calls in template

    // Audio player state
    audioUrl: string | null = null;
    currentSongTitle: string = '';
    isPlaying = false;
    currentTime = 0;
    duration = 0;
    volume = 1;
    isMuted = false;
    isLoaded = false;

    @ViewChild(SongDetailPanelComponent) songDetailPanel!: SongDetailPanelComponent;
    @ViewChild('audioPlayer') audioPlayer!: ElementRef<HTMLAudioElement>;

    private fb = inject(FormBuilder);
    private songService = inject(SongService);
    private apiConfig = inject(ApiConfigService);
    private notificationService = inject(NotificationService);
    private chatService = inject(ChatService);
    private progressService = inject(ProgressService);
    private dialog = inject(MatDialog);
    private architectureService = inject(LyricArchitectureService);
    private musicStyleChooserService = inject(MusicStyleChooserService);
    private translate = inject(TranslateService);

    ngOnInit() {
        this.songForm = this.fb.group({
            lyrics: ['', Validators.required],
            prompt: ['', Validators.required],
            model: ['auto', Validators.required],
            title: ['', [Validators.maxLength(50)]],
            isInstrumental: [false]
        });

        // Load saved form data
        const savedData = this.songService.loadFormData();
        if (savedData.lyrics || savedData.isInstrumental || savedData.title) {
            this.songForm.patchValue(savedData);
        }

        // Initialize isInstrumentalMode property
        this.isInstrumentalMode = this.songForm.get('isInstrumental')?.value || false;

        // Update validators when isInstrumental changes
        this.songForm.get('isInstrumental')?.valueChanges.subscribe(isInstrumental => {
            this.isInstrumentalMode = isInstrumental; // Update computed property
            this.updateValidators(isInstrumental);
        });

        // Save form data on changes
        this.songForm.valueChanges.subscribe(value => {
            this.songService.saveFormData(value);
        });

        // Initialize validators based on current state
        this.updateValidators(this.songForm.get('isInstrumental')?.value || false);
    }

    async onSubmit() {
        if (this.songForm.valid) {
            const isInstrumental = this.songForm.get('isInstrumental')?.value;
            if (isInstrumental) {
                await this.generateInstrumental();
            } else {
                await this.generateSong();
            }
        }
    }

    resetForm() {
        this.songForm.reset({model: 'auto', isInstrumental: false});
        this.isInstrumentalMode = false; // Reset computed property
        this.songService.clearFormData();
        this.result = '';
    }


    async generateSong() {
        const formValue = this.songForm.value;
        this.isLoading = true;
        this.result = '';

        try {
            const data = await this.songService.generateSong(
                formValue.lyrics.trim(),
                formValue.prompt.trim(),
                formValue.model,
                formValue.title?.trim() || undefined
            );

            if (data.task_id) {
                // Store song_id if provided by backend
                if (data.song_id) {
                    this.currentSongId = data.song_id;
                }
                await this.checkSongStatus(data.task_id, false);
            } else {
                const errorMsg = this.translate.instant('songGenerator.errors.errorInitSong');
                this.notificationService.error(errorMsg);
                this.result = errorMsg;
            }
        } catch (err: any) {
            this.notificationService.error(`Error: ${err.message}`);
            this.result = `Error: ${err.message}`;
        }
    }

    async generateInstrumental() {
        const formValue = this.songForm.value;
        this.isLoading = true;
        this.result = '';

        try {
            const data = await this.songService.generateInstrumental(
                formValue.title.trim(),
                formValue.prompt.trim(),
                formValue.model
            );

            if (data.task_id) {
                // Store song_id if provided by backend
                if (data.song_id) {
                    this.currentSongId = data.song_id;
                }
                await this.checkSongStatus(data.task_id, true);
            } else {
                const errorMsg = this.translate.instant('songGenerator.errors.errorInitInstrumental');
                this.notificationService.error(errorMsg);
                this.result = errorMsg;
            }
        } catch (err: any) {
            this.notificationService.error(`Error: ${err.message}`);
            this.result = `Error: ${err.message}`;
        }
    }

    async checkSongStatus(taskId: string, isInstrumental: boolean = false) {
        let completed = false;
        let interval = 5000;

        while (!completed) {
            try {
                const data = isInstrumental
                    ? await this.songService.checkInstrumentalStatus(taskId)
                    : await this.songService.checkSongStatus(taskId);

                if (data.status === 'SUCCESS') {
                    await this.renderResultTask(data.result);
                    completed = true;
                } else if (data.status === 'FAILURE') {
                    const errorKey = isInstrumental ? 'songGenerator.errors.instrumentalFailed' : 'songGenerator.errors.generationFailed';
                    const errorMessage = data.result?.error || data.result || this.translate.instant(errorKey);
                    this.notificationService.error(`${this.translate.instant(errorKey)}: ${errorMessage}`);
                    this.result = `<div class="error-box">Error: ${errorMessage}</div>`;
                    completed = true;
                } else {
                    const statusText = this.getStatusText(data);
                    this.loadingMessage = statusText;
                    interval = Math.min(interval * 1.5, 60000);
                    await new Promise(resolve => setTimeout(resolve, interval));
                }
            } catch (error: any) {
                const errorMsg = this.translate.instant('songGenerator.errors.errorFetchingStatus');
                this.notificationService.error(`${errorMsg}: ${error.message}`);
                this.result = `${errorMsg}: ${error.message}`;
                completed = true;
            }
        }

        this.isLoading = false;
    }

    async renderResultTask(data: any): Promise<void> {
        // Only use DB loading - no more MUREKA result fallback
        if (this.currentSongId && (data.status === 'SUCCESS' || data.status === 'succeeded')) {
            this.result = '';
            // Einfach das Detail Panel refreshen - Daten sind bereits in DB
            if (this.songDetailPanel) {
                // Sicherstellen dass die songId gesetzt ist bevor wir reloadSong aufrufen
                this.songDetailPanel.songId = this.currentSongId;
                await this.songDetailPanel.reloadSong();
            }
            return;
        } else if (data.status === 'FAILURE') {
            // Nur bei FAILURE Fehler zeigen
            this.result = 'Error: Song generation failed.';
            this.notificationService.error('Song generation failed');
        }
    }



    // Event handlers for song detail panel
    onPlayAudio(event: {url: string, id: string, choiceNumber: number}) {
        this.onPlayAudioInternal(event.url, event.id);
    }

    // Audio methods
    onPlayAudioInternal(url: string, id: string) {
        if (this.currentlyPlaying === id) {
            this.stopAudio();
        } else {
            this.playAudioInternal(url, id);
        }
    }

    private playAudioInternal(mp3Url: string, choiceId: string) {
        this.audioUrl = mp3Url;
        this.currentlyPlaying = choiceId;
        // Get song title from current song via song detail panel
        const currentSong = this.songDetailPanel?.song;
        const songTitle = currentSong?.title || 'Generated Song';
        this.currentSongTitle = songTitle.length > 40 ? songTitle.substring(0, 37) + '...' : songTitle;

        // Wait for audio element to be ready
        setTimeout(() => {
            if (this.audioPlayer?.nativeElement) {
                this.audioPlayer.nativeElement.volume = this.volume;
                this.audioPlayer.nativeElement.play();
            }
        }, 100);
    }

    playPauseAudio() {
        if (!this.audioPlayer?.nativeElement) return;

        if (this.isPlaying) {
            this.audioPlayer.nativeElement.pause();
        } else {
            this.audioPlayer.nativeElement.play();
        }
    }

    stopAudio() {
        if (this.audioPlayer?.nativeElement) {
            this.audioPlayer.nativeElement.pause();
            this.audioPlayer.nativeElement.currentTime = 0;
        }
        this.currentlyPlaying = null;
        this.audioUrl = null;
        this.isPlaying = false;
        this.currentTime = 0;
        this.isLoaded = false;
    }

    onTimeUpdate() {
        if (this.audioPlayer?.nativeElement) {
            this.currentTime = this.audioPlayer.nativeElement.currentTime;
            this.duration = this.audioPlayer.nativeElement.duration || 0;
        }
    }

    onLoadedMetadata() {
        if (this.audioPlayer?.nativeElement) {
            this.duration = this.audioPlayer.nativeElement.duration;
            this.isLoaded = true;
        }
    }

    onPlay() {
        this.isPlaying = true;
    }

    onPause() {
        this.isPlaying = false;
    }

    onSeek(event: Event) {
        const target = event.target as HTMLInputElement;
        const seekTime = parseFloat(target.value);
        if (this.audioPlayer?.nativeElement) {
            this.audioPlayer.nativeElement.currentTime = seekTime;
        }
    }

    toggleMute() {
        if (!this.audioPlayer?.nativeElement) return;

        this.isMuted = !this.isMuted;
        this.audioPlayer.nativeElement.muted = this.isMuted;
    }

    onVolumeChange(event: Event) {
        const target = event.target as HTMLInputElement;
        this.volume = parseFloat(target.value);
        if (this.audioPlayer?.nativeElement) {
            this.audioPlayer.nativeElement.volume = this.volume;
        }
    }

    formatTime(seconds: number): string {
        if (isNaN(seconds)) return '0:00';
        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = Math.floor(seconds % 60);
        return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
    }

    onDownloadStems(url: string) {
        this.downloadStems(url);
    }

    onCopyLyrics() {
        // No-op: Panel handles this internally
    }

    private delay(ms: number): Promise<void> {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    private getStatusText(data: any): string {
        // Check for specific internal progress statuses first
        if (data.progress?.status) {
            switch (data.progress.status) {
                case 'SLOT_ACQUIRED':
                    return this.translate.instant('songGenerator.status.acquiring');
                case 'GENERATION_STARTED':
                    return this.translate.instant('songGenerator.status.starting');
                case 'POLLING':
                    return this.translate.instant('songGenerator.status.polling');
                default:
                    break;
            }
        }

        // Check for mureka-specific status
        if (data.progress?.mureka_status) {
            switch (data.progress.mureka_status) {
                case 'preparing':
                    return this.translate.instant('songGenerator.status.preparing');
                case 'queued':
                    return this.translate.instant('songGenerator.status.queued');
                case 'running':
                    return this.translate.instant('songGenerator.status.generatingAi');
                case 'timeouted':
                    return this.translate.instant('songGenerator.status.timeout');
                default:
                    return `${this.translate.instant('songGenerator.status.polling')} (${data.progress.mureka_status})`;
            }
        }

        // Fallback to general celery status
        switch (data.status) {
            case 'PENDING':
                return this.translate.instant('songGenerator.status.initializing');
            case 'PROGRESS':
                return this.translate.instant('songGenerator.status.processingRequest');
            default:
                return this.translate.instant('songGenerator.status.processing');
        }
    }

    downloadFlac(flacUrl: string) {
        // Create a temporary anchor element to trigger the download
        const link = document.createElement('a');
        link.href = flacUrl;
        link.download = ''; // This will use the filename from the URL
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }

    downloadStems(stemsUrl: string) {
        // Create a temporary anchor element to trigger the download
        const link = document.createElement('a');
        link.href = stemsUrl;
        link.download = ''; // This will use the filename from the URL
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }


    // Handlers for shared song detail panel - now handled directly by the shared component
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    onTitleChanged(_newTitle: string) {
        // No-op: Shared component handles this
    }

    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    onTagsChanged(_newTags: string[]) {
        // No-op: Shared component handles this
    }

    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    onWorkflowChanged(_newWorkflow: string) {
        // No-op: Shared component handles this
    }

    onDownloadFlac(url: string) {
        this.downloadFlac(url);
    }


    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    onUpdateRating(_event: { choiceId: string, rating: number | null }) {
        // No-op: Shared component handles this
    }

    async improvePrompt() {
        const currentPrompt = this.songForm.get('prompt')?.value?.trim();
        if (!currentPrompt) {
            this.notificationService.error(this.translate.instant('songGenerator.errors.promptRequired'));
            return;
        }

        this.isImprovingPrompt = true;
        try {
            const improvedPrompt = await this.progressService.executeWithProgress(
                () => this.chatService.improveMusicStylePrompt(currentPrompt),
                this.translate.instant('songGenerator.progress.enhancing'),
                this.translate.instant('songGenerator.progress.enhancinghint')
            );
            this.songForm.patchValue({prompt: this.removeQuotes(improvedPrompt)});
        } catch (error: any) {
            this.notificationService.error(`Error improving prompt: ${error.message}`);
        } finally {
            this.isImprovingPrompt = false;
        }
    }

    async generateLyrics() {
        const currentText = this.songForm.get('lyrics')?.value?.trim();
        if (!currentText) {
            this.notificationService.error(this.translate.instant('songGenerator.errors.textRequired'));
            return;
        }

        this.isGeneratingLyrics = true;
        try {
            const generatedLyrics = await this.progressService.executeWithProgress(
                () => this.chatService.generateLyrics(currentText),
                this.translate.instant('songGenerator.progress.generatingLyrics'),
                this.translate.instant('songGenerator.progress.generatingLyricsHint')
            );
            this.songForm.patchValue({lyrics: this.removeQuotes(generatedLyrics)});
        } catch (error: any) {
            this.notificationService.error(`Error generating lyrics: ${error.message}`);
        } finally {
            this.isGeneratingLyrics = false;
        }
    }

    async translateLyrics() {
        const currentLyrics = this.songForm.get('lyrics')?.value?.trim();
        if (!currentLyrics) {
            this.notificationService.error(this.translate.instant('songGenerator.errors.lyricsRequired'));
            return;
        }

        this.isTranslatingLyrics = true;
        try {
            const translatedLyrics = await this.progressService.executeWithProgress(
                () => this.chatService.translateLyric(currentLyrics),
                this.translate.instant('songGenerator.progress.translatingLyrics'),
                this.translate.instant('songGenerator.progress.translatingLyricsHint')
            );
            this.songForm.patchValue({lyrics: this.removeQuotes(translatedLyrics)});
        } catch (error: any) {
            this.notificationService.error(`Error translating lyrics: ${error.message}`);
        } finally {
            this.isTranslatingLyrics = false;
        }
    }

    toggleLyricsDropdown() {
        this.showLyricsDropdown = !this.showLyricsDropdown;
    }

    closeLyricsDropdown() {
        this.showLyricsDropdown = false;
    }

    selectLyricsAction(action: 'generate' | 'translate' | 'architecture') {
        this.closeLyricsDropdown();

        if (action === 'generate') {
            this.generateLyrics();
        } else if (action === 'translate') {
            this.translateLyrics();
        } else if (action === 'architecture') {
            this.openLyricArchitectModal();
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

    openMusicStyleChooserModal(): void {
        const isInstrumental = this.isInstrumentalMode; // Use property instead of method call
        const dialogRef = this.dialog.open(MusicStyleChooserModalComponent, {
            width: '1100px',
            maxWidth: '95vw',
            maxHeight: '90vh',
            disableClose: false,
            autoFocus: true,
            data: { isInstrumental }
        });

        dialogRef.afterClosed().subscribe(result => {
            if (result && result.stylePrompt) {
                const currentPrompt = this.songForm.get('prompt')?.value?.trim();

                // Warn if textarea is filled - ONLY when user confirms the dialog
                if (currentPrompt) {
                    const confirmOverwrite = confirm(this.translate.instant('songGenerator.styleChooserOverwriteWarning'));
                    if (!confirmOverwrite) {
                        return;
                    }
                }

                // Apply the generated style prompt to the form
                this.songForm.patchValue({
                    prompt: result.stylePrompt
                });
                this.notificationService.success(this.translate.instant('songGenerator.success.styleApplied'));
            }
        });
    }

    toggleStyleDropdown() {
        this.showStyleDropdown = !this.showStyleDropdown;
    }

    closeStyleDropdown() {
        this.showStyleDropdown = false;
    }

    selectStyleAction(action: 'enhance' | 'translate' | 'chooser') {
        this.closeStyleDropdown();

        if (action === 'enhance') {
            this.improvePrompt();
        } else if (action === 'translate') {
            this.translateStylePrompt();
        } else if (action === 'chooser') {
            this.openMusicStyleChooserModal();
        }
    }

    async translateStylePrompt() {
        const currentPrompt = this.songForm.get('prompt')?.value?.trim();
        if (!currentPrompt) {
            this.notificationService.error(this.translate.instant('songGenerator.errors.promptRequired'));
            return;
        }

        this.isTranslatingStylePrompt = true;
        try {
            const translatedPrompt = await this.progressService.executeWithProgress(
                () => this.chatService.translateMusicStylePrompt(currentPrompt),
                this.translate.instant('songGenerator.progress.translatingPrompt'),
                this.translate.instant('songGenerator.progress.translatingPromptHint')
            );
            this.songForm.patchValue({prompt: this.removeQuotes(translatedPrompt)});
        } catch (error: any) {
            this.notificationService.error(`Error translating style prompt: ${error.message}`);
        } finally {
            this.isTranslatingStylePrompt = false;
        }
    }

    @HostListener('document:click', ['$event'])
    onDocumentClick(event: Event) {
        const target = event.target as HTMLElement;
        const lyricsDropdown = target.closest('.lyrics-dropdown-container');
        const styleDropdown = target.closest('.style-dropdown-container');
        const titleDropdown = target.closest('.title-dropdown-container');

        if (!lyricsDropdown && this.showLyricsDropdown) {
            this.closeLyricsDropdown();
        }

        if (!styleDropdown && this.showStyleDropdown) {
            this.closeStyleDropdown();
        }

        if (!titleDropdown && this.showTitleDropdown) {
            this.closeTitleDropdown();
        }
    }


    private removeQuotes(text: string): string {
        if (!text) return text;
        return text.replace(/^["']|["']$/g, '').trim();
    }

    private updateValidators(isInstrumental: boolean) {
        const lyricsControl = this.songForm.get('lyrics');
        const titleControl = this.songForm.get('title');

        if (isInstrumental) {
            // For instrumental: lyrics not required, title is required
            lyricsControl?.clearValidators();
            titleControl?.setValidators([Validators.required, Validators.maxLength(50)]);
        } else {
            // For normal songs: lyrics required, title optional
            lyricsControl?.setValidators([Validators.required]);
            titleControl?.setValidators([Validators.maxLength(50)]);
        }

        lyricsControl?.updateValueAndValidity();
        titleControl?.updateValueAndValidity();
    }

    isInstrumental(): boolean {
        return this.songForm.get('isInstrumental')?.value || false;
    }

    setMode(mode: 'song' | 'instrumental') {
        const isInstrumental = mode === 'instrumental';
        this.isInstrumentalMode = isInstrumental; // Update computed property
        this.songForm.patchValue({isInstrumental: isInstrumental});
    }

    async generateTitle() {
        const isInstrumental = this.isInstrumentalMode; // Use property instead of method call
        let inputText = '';

        // Priority logic: Title > Lyrics (non-instrumental) / Style (instrumental) > Fallback
        const currentTitle = this.songForm.get('title')?.value?.trim();
        const currentLyrics = this.songForm.get('lyrics')?.value?.trim();
        const currentStyle = this.songForm.get('prompt')?.value?.trim();

        if (currentTitle) {
            inputText = currentTitle;
        } else if (isInstrumental && currentStyle) {
            // For instrumental: use style prompt
            inputText = currentStyle;
        } else if (!isInstrumental && currentLyrics) {
            // For regular songs: use lyrics
            inputText = currentLyrics;
        } else {
            // Fallback constant
            inputText = this.translate.instant('songGenerator.generateTitleFallback');
        }

        this.isGeneratingTitle = true;
        try {
            const generatedTitle = await this.progressService.executeWithProgress(
                () => this.chatService.generateTitle(inputText),
                this.translate.instant('songGenerator.progress.generatingTitle'),
                this.translate.instant('songGenerator.progress.generatingTitleHint')
            );
            this.songForm.patchValue({title: this.removeQuotes(generatedTitle)});
        } catch (error: any) {
            this.notificationService.error(`Error generating title: ${error.message}`);
        } finally {
            this.isGeneratingTitle = false;
        }
    }

    toggleTitleDropdown() {
        this.showTitleDropdown = !this.showTitleDropdown;
    }

    closeTitleDropdown() {
        this.showTitleDropdown = false;
    }

    selectTitleAction(action: 'generate') {
        this.closeTitleDropdown();

        if (action === 'generate') {
            this.generateTitle();
        }
    }
}
