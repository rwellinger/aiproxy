import {Component, OnInit, ViewEncapsulation, inject, HostListener, ViewChild, ElementRef} from '@angular/core';
import {FormBuilder, FormGroup, FormsModule, ReactiveFormsModule, Validators} from '@angular/forms';
import {CommonModule} from '@angular/common';
import {Router, ActivatedRoute} from '@angular/router';
import {TranslateModule, TranslateService} from '@ngx-translate/core';
import {firstValueFrom} from 'rxjs';
import {SongService} from '../../services/business/song.service';
import {SketchService, Sketch} from '../../services/business/sketch.service';
import {ApiConfigService} from '../../services/config/api-config.service';
import {HealthService} from '../../services/config/health.service';
import {NotificationService} from '../../services/ui/notification.service';
import {ChatService} from '../../services/config/chat.service';
import {MatSnackBarModule} from '@angular/material/snack-bar';
import {MatCardModule} from '@angular/material/card';
import {SongDetailPanelComponent} from '../../components/song-detail-panel/song-detail-panel.component';
import {ProgressService} from '../../services/ui/progress.service';

@Component({
    selector: 'app-song-generator',
    standalone: true,
    imports: [CommonModule, FormsModule, ReactiveFormsModule, MatSnackBarModule, MatCardModule, SongDetailPanelComponent, TranslateModule],
    templateUrl: './song-generator.component.html',
    styleUrl: './song-generator.component.scss',
    encapsulation: ViewEncapsulation.None
})
export class SongGeneratorComponent implements OnInit {
    songForm!: FormGroup;
    isLoading = false;
    isGeneratingTitle = false;
    showTitleDropdown = false;
    loadingMessage = '';
    result = '';
    currentlyPlaying: string | null = null;
    currentSongId: string | null = null;
    isInstrumentalMode = false; // Computed property to avoid method calls in template

    // Sketch selection
    sketches: Sketch[] = [];
    selectedSketch: Sketch | null = null;
    selectedSketchId: string | null = null;

    // Storage health state (preventive UX)
    isStorageHealthy = true;
    isCheckingStorage = true;

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
    private sketchService = inject(SketchService);
    private apiConfig = inject(ApiConfigService);
    private healthService = inject(HealthService);
    private notificationService = inject(NotificationService);
    private chatService = inject(ChatService);
    private progressService = inject(ProgressService);
    private translate = inject(TranslateService);
    private router = inject(Router);
    private route = inject(ActivatedRoute);

    ngOnInit() {
        this.songForm = this.fb.group({
            lyrics: ['', Validators.required],
            prompt: ['', [Validators.required, Validators.maxLength(1024)]],
            model: ['auto', Validators.required],
            title: ['', [Validators.maxLength(50)]],
            isInstrumental: [false]
        });

        // Initialize isInstrumentalMode property
        this.isInstrumentalMode = this.songForm.get('isInstrumental')?.value || false;

        // Update validators when isInstrumental changes
        this.songForm.get('isInstrumental')?.valueChanges.subscribe(isInstrumental => {
            this.isInstrumentalMode = isInstrumental; // Update computed property
            this.updateValidators(isInstrumental);
        });

        // Initialize validators based on current state
        this.updateValidators(this.songForm.get('isInstrumental')?.value || false);

        // Load sketches
        this.loadSketches();

        // Check for sketch_id in URL
        this.route.queryParams.subscribe(params => {
            if (params['sketch_id']) {
                this.loadSketchById(params['sketch_id']);
            }
        });

        // CRITICAL: Check storage health on page load (preventive UX)
        // Disables generate button if MinIO is down (prevents wasted API credits)
        this.checkStorageHealth();
    }

    /**
     * Check storage health on component init
     * Prevents users from wasting API credits when storage is unavailable
     */
    private async checkStorageHealth() {
        this.isCheckingStorage = true;
        try {
            this.isStorageHealthy = await firstValueFrom(this.healthService.checkStorage());
        } catch (error) {
            console.warn('[SongGenerator] Storage health check failed:', error);
            this.isStorageHealthy = false;
        } finally {
            this.isCheckingStorage = false;
        }
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
                formValue.title?.trim() || undefined,
                this.selectedSketch?.id || undefined
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
                formValue.model,
                this.selectedSketch?.id || undefined
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

                    // Refresh detail panel to show FAILURE status from DB
                    if (this.songDetailPanel && this.currentSongId) {
                        this.songDetailPanel.songId = this.currentSongId;
                        await this.songDetailPanel.reloadSong();
                    }

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

    @HostListener('document:click', ['$event'])
    onDocumentClick(event: Event) {
        const target = event.target as HTMLElement;
        const titleDropdown = target.closest('.title-dropdown-container');

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

    // Sketch-related methods
    async loadSketches(): Promise<void> {
        try {
            const response = await firstValueFrom(
                this.sketchService.getSketches(100, 0, 'draft', undefined, 'song')
            );
            this.sketches = response.data || [];
        } catch (error: any) {
            console.error('Error loading sketches:', error);
        }
    }

    async loadSketchById(sketchId: string): Promise<void> {
        try {
            const response = await firstValueFrom(
                this.sketchService.getSketchById(sketchId)
            );
            if (response.data) {
                this.onSketchSelected(response.data);
            }
        } catch (error: any) {
            this.notificationService.error(
                this.translate.instant('songGenerator.errors.sketchNotFound')
            );
        }
    }

    onSketchIdChanged(sketchId: string | null): void {
        if (!sketchId) {
            this.clearSketch();
            return;
        }

        const sketch = this.sketches.find(s => s.id === sketchId);
        if (sketch) {
            this.onSketchSelected(sketch);
        }
    }

    onSketchSelected(sketch: Sketch): void {
        this.selectedSketch = sketch;
        this.selectedSketchId = sketch.id;
        this.songForm.patchValue({
            title: sketch.title || '',
            lyrics: sketch.lyrics || '',
            prompt: sketch.prompt || ''
        });
        this.notificationService.success(
            this.translate.instant('songGenerator.success.sketchLoaded')
        );
    }

    clearSketch(): void {
        this.selectedSketch = null;
        this.selectedSketchId = null;

        // Clear form fields
        this.songForm.patchValue({
            title: '',
            lyrics: '',
            prompt: ''
        });

        this.notificationService.success(
            this.translate.instant('songGenerator.success.sketchCleared')
        );
    }

    getSketchWorkflowLabel(workflow: string | undefined): string {
        if (!workflow) return '';
        return this.translate.instant(`songSketch.workflow.${workflow}`);
    }
}
