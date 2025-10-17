import {Component, OnInit, ViewEncapsulation, inject, HostListener} from '@angular/core';
import {FormBuilder, FormGroup, ReactiveFormsModule, FormsModule} from '@angular/forms';
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
import {SongSection, SongSectionItem} from '../../models/lyric-architecture.model';

interface LyricSection {
    id: string;
    label: string;
    content: string;
    order: number;
}

@Component({
    selector: 'app-lyric-creation',
    standalone: true,
    imports: [CommonModule, ReactiveFormsModule, FormsModule, MatSnackBarModule, MatCardModule, TranslateModule],
    templateUrl: './lyric-creation.component.html',
    styleUrl: './lyric-creation.component.scss',
    encapsulation: ViewEncapsulation.None
})
export class LyricCreationComponent implements OnInit {
    lyricForm!: FormGroup;
    isGeneratingLyrics = false;
    isTranslatingLyrics = false;
    showTextToolsDropdown = false;
    lastCleanupState: string | null = null;
    lastStructureState: string | null = null;

    // Section Editor State
    sectionEditorMode = false;
    sections: LyricSection[] = [];
    activeSection: LyricSection | null = null;
    lastSectionState: string | null = null;
    isImprovingSection = false;
    isRewritingSection = false;
    isExtendingSection = false;

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

    private capitalizeLabel(label: string): string {
        // Capitalize first letter and letters after hyphens
        // Examples: PRE-CHORUS -> Pre-Chorus, VERSE1 -> Verse1, POST_CHORUS -> Post-Chorus
        const normalized = label.replace(/_/g, '-').toLowerCase();
        return normalized.replace(/(^|-)(\w)/g, (match, separator, letter) =>
            separator + letter.toUpperCase()
        );
    }

    get characterCount(): number {
        return this.lyricForm.get('lyrics')?.value?.length || 0;
    }

    get canUndo(): boolean {
        return this.lastCleanupState !== null || this.lastStructureState !== null;
    }

    get hasSections(): boolean {
        const lyrics = this.lyricForm.get('lyrics')?.value || '';
        // Match both formats: **Label** (Markdown) and Label: (classic)
        return /^(\*\*\s*(Intro|Verse\s*\d+|Chorus|Bridge|Outro|Pre[-_\s]?chorus|Post[-_\s]?chorus)\s*\*\*|(Intro|Verse\d+|Chorus|Bridge|Outro|Pre[-_]?chorus|Post[-_]?chorus):)/mi.test(lyrics);
    }

    toggleTextToolsDropdown() {
        this.showTextToolsDropdown = !this.showTextToolsDropdown;
    }

    closeTextToolsDropdown() {
        this.showTextToolsDropdown = false;
    }

    selectTextToolAction(action: 'cleanup' | 'structure' | 'undo' | 'sectionEditor' | 'rebuild') {
        this.closeTextToolsDropdown();

        if (action === 'cleanup') {
            this.cleanupLyrics();
        } else if (action === 'structure') {
            this.applyStructure();
        } else if (action === 'undo') {
            this.undoLastChange();
        } else if (action === 'sectionEditor') {
            this.toggleSectionEditor();
        } else if (action === 'rebuild') {
            this.rebuildFromLyricText();
        }
    }

    cleanupLyrics(): void {
        let lyrics = this.lyricForm.get('lyrics')?.value || '';
        if (!lyrics.trim()) {
            return;
        }

        // Save current state before cleanup
        this.lastCleanupState = lyrics;

        // 1. Remove trailing spaces from each line
        lyrics = lyrics.replace(/\s+$/gm, '');

        // 2. Normalize non-ASCII characters
        const replacements: Record<string, string> = {
            '\u201C': '"', '\u201D': '"', '\u2018': "'", '\u2019': "'",
            '\u2014': ' - ', '\u2013': ' - ', '\u2026': '...'
        };
        Object.keys(replacements).forEach(char => {
            lyrics = lyrics.replace(new RegExp(char, 'g'), replacements[char]);
        });

        // 3. Add line breaks after commas and periods
        lyrics = lyrics.replace(/,\s+/g, ',\n');
        lyrics = lyrics.replace(/\.\s+/g, '.\n');

        // 4. Clean up multiple consecutive blank lines (keep max 2 newlines = 1 blank line)
        // This preserves paragraph separation but removes excessive spacing
        lyrics = lyrics.replace(/\n{3,}/g, '\n\n');

        this.lyricForm.patchValue({lyrics: lyrics.trim()});
        this.notificationService.success(this.translate.instant('lyricCreation.cleanupComplete'));
    }

    applyStructure(): void {
        let lyrics = this.lyricForm.get('lyrics')?.value || '';
        if (!lyrics.trim()) {
            this.notificationService.error(this.translate.instant('lyricCreation.errors.lyricsRequired'));
            return;
        }

        // Check if labels already exist (various formats: Label:, [Label], **LABEL**, etc.)
        const hasLabels = /^(\w+:|[*[\]]).*$/m.test(lyrics);
        if (hasLabels) {
            const confirmed = confirm(this.translate.instant('lyricCreation.confirmApplyStructure'));
            if (!confirmed) {
                return;
            }
        }

        // Get architecture from service
        const architectureString = this.architectureService.generateArchitectureString();
        if (!architectureString || !architectureString.trim()) {
            this.notificationService.error(this.translate.instant('lyricCreation.errors.noArchitecture'));
            return;
        }

        // Parse architecture: Extract only the elements (INTRO, VERSE1, etc.)
        // Format is: "Song structure: INTRO - VERSE1 - CHORUS - ..."
        const match = architectureString.match(/song structure:\s*(.+)/i);
        if (!match) {
            this.notificationService.error(this.translate.instant('lyricCreation.errors.noArchitecture'));
            return;
        }

        // Split by " - " and clean up
        const sections = match[1].split('-').map((s: string) => s.trim()).filter((s: string) => s);
        if (sections.length === 0) {
            this.notificationService.error(this.translate.instant('lyricCreation.errors.noArchitecture'));
            return;
        }

        // Save current state before applying structure
        this.lastStructureState = lyrics;

        // Remove existing labels from lyrics (various formats)
        // Match labels like: Intro:, Verse1:, Pre-Chorus:, Post-Chorus:, etc.
        lyrics = lyrics.replace(/^([\w-]+:|[*[\]].*|)$/gm, '');
        lyrics = lyrics.replace(/^\*{2}[A-Z\s-]+\*{2}\s*/gm, '');
        lyrics = lyrics.replace(/^[A-Z][a-z-]*\d*:\s*/gm, '');

        // Split into paragraphs (separated by blank lines)
        const paragraphs = lyrics.split(/\n\s*\n/).filter((p: string) => p.trim());

        if (paragraphs.length === 0) {
            this.notificationService.error(this.translate.instant('lyricCreation.errors.lyricsRequired'));
            return;
        }

        // Apply structure: 1:1 mapping with Markdown bold format "**Label**\nText"
        const structured = paragraphs.map((para: string, i: number) => {
            if (i < sections.length) {
                // Capitalize properly (e.g., VERSE1 -> Verse1, PRE-CHORUS -> Pre-Chorus)
                const label = this.capitalizeLabel(sections[i]);
                return `**${label}**\n${para.trim()}`;
            }
            return para.trim();
        }).join('\n\n');

        this.lyricForm.patchValue({lyrics: structured});
        this.notificationService.success(this.translate.instant('lyricCreation.structureApplied'));
    }

    undoLastChange(): void {
        if (this.lastStructureState !== null) {
            // Undo structure change (most recent)
            this.lyricForm.patchValue({lyrics: this.lastStructureState});
            this.lastStructureState = null;
            this.notificationService.success(this.translate.instant('lyricCreation.undoApplied'));
        } else if (this.lastCleanupState !== null) {
            // Undo cleanup change
            this.lyricForm.patchValue({lyrics: this.lastCleanupState});
            this.lastCleanupState = null;
            this.notificationService.success(this.translate.instant('lyricCreation.undoApplied'));
        }
    }

    private parseLyrics(text: string): LyricSection[] {
        const sections: LyricSection[] = [];
        // Regex to match section labels in both formats:
        // 1. **Label** (Markdown bold) - with optional spaces: **Verse 1**, **INTRO**, **Pre-Chorus**
        // 2. Label: (classic) - Verse1:, Intro:, Pre-Chorus:
        const sectionRegex = /^(\*\*\s*(Intro|Verse\s*\d+|Chorus|Bridge|Outro|Pre[-_\s]?chorus|Post[-_\s]?chorus)\s*\*\*|(Intro|Verse\d+|Chorus|Bridge|Outro|Pre[-_]?chorus|Post[-_]?chorus):)\s*$/gmi;
        const lines = text.split('\n');
        let currentSection: LyricSection | null = null;
        let order = 0;

        for (const line of lines) {
            const match = sectionRegex.exec(line);

            if (match) {
                // Found a section label
                if (currentSection) {
                    // Save previous section
                    sections.push(currentSection);
                }

                // Extract label from either format
                // match[2] = Markdown format (inside **...** )
                // match[3] = Classic format (before :)
                let rawLabel = match[2] || match[3];

                // Normalize: Remove spaces before numbers (Verse 1 -> Verse1)
                rawLabel = rawLabel.replace(/\s+(\d+)/g, '$1');
                // Normalize: Convert underscores to hyphens (Pre_Chorus -> Pre-Chorus)
                rawLabel = rawLabel.replace(/_/g, '-');

                // Start new section - normalize label with proper capitalization
                const label = this.capitalizeLabel(rawLabel);
                currentSection = {
                    id: `section-${order}-${Date.now()}`,
                    label: label,
                    content: '',
                    order: order++
                };

                // Reset regex lastIndex for next iteration
                sectionRegex.lastIndex = 0;
            } else if (currentSection) {
                // Add line to current section content
                if (currentSection.content) {
                    currentSection.content += '\n' + line;
                } else {
                    currentSection.content = line;
                }
            }
        }

        // Save last section
        if (currentSection) {
            sections.push(currentSection);
        }

        // Clean up content (trim whitespace)
        sections.forEach(section => {
            section.content = section.content.trim();
        });

        return sections;
    }

    private rebuildLyrics(sections: LyricSection[]): string {
        return sections
            .sort((a, b) => a.order - b.order)
            .map(section => `**${section.label}**\n${section.content}`)
            .join('\n\n');
    }

    toggleSectionEditor(): void {
        if (!this.hasSections) {
            const confirmed = confirm(
                this.translate.instant('lyricCreation.sectionEditor.noStructure')
            );
            if (confirmed) {
                this.applyStructure();
                setTimeout(() => this.toggleSectionEditor(), 100);
            }
            return;
        }

        const currentLyrics = this.lyricForm.get('lyrics')?.value || '';
        this.lastSectionState = currentLyrics;
        this.sections = this.parseLyrics(currentLyrics);

        if (this.sections.length === 0) {
            this.notificationService.error(
                this.translate.instant('lyricCreation.sectionEditor.parseFailed')
            );
            return;
        }

        this.sectionEditorMode = true;
        this.activeSection = this.sections[0];
        this.notificationService.info(
            this.translate.instant('lyricCreation.sectionEditor.activated')
        );
    }

    applyAndCloseSectionEditor(): void {
        const updatedLyrics = this.rebuildLyrics(this.sections);
        this.lyricForm.patchValue({ lyrics: updatedLyrics });

        this.sectionEditorMode = false;
        this.activeSection = null;

        this.notificationService.success(
            this.translate.instant('lyricCreation.sectionEditor.applied')
        );
    }

    cancelSectionEditor(): void {
        if (this.lastSectionState) {
            this.lyricForm.patchValue({ lyrics: this.lastSectionState });
        }

        this.sectionEditorMode = false;
        this.activeSection = null;

        this.notificationService.info(
            this.translate.instant('lyricCreation.sectionEditor.cancelled')
        );
    }

    selectSection(section: LyricSection): void {
        this.activeSection = section;
    }

    async improveSectionAI(): Promise<void> {
        if (!this.activeSection) {
            return;
        }

        this.isImprovingSection = true;
        try {
            const fullContext = this.rebuildLyrics(this.sections);
            const improvedContent = await this.progressService.executeWithProgress(
                () => this.chatService.improveLyricSection(
                    this.activeSection!.label,
                    this.activeSection!.content,
                    fullContext
                ),
                this.translate.instant('lyricCreation.sectionEditor.improving'),
                this.translate.instant('lyricCreation.sectionEditor.improvingHint')
            );
            this.activeSection.content = this.removeQuotes(improvedContent);
        } catch (error: any) {
            this.notificationService.error(`Error improving section: ${error.message}`);
        } finally {
            this.isImprovingSection = false;
        }
    }

    async rewriteSectionAI(): Promise<void> {
        if (!this.activeSection) {
            return;
        }

        this.isRewritingSection = true;
        try {
            const rewrittenContent = await this.progressService.executeWithProgress(
                () => this.chatService.rewriteLyricSection(this.activeSection!.content),
                this.translate.instant('lyricCreation.sectionEditor.rewriting'),
                this.translate.instant('lyricCreation.sectionEditor.rewritingHint')
            );
            this.activeSection.content = this.removeQuotes(rewrittenContent);
        } catch (error: any) {
            this.notificationService.error(`Error rewriting section: ${error.message}`);
        } finally {
            this.isRewritingSection = false;
        }
    }

    async extendSectionAI(): Promise<void> {
        if (!this.activeSection) {
            return;
        }

        this.isExtendingSection = true;
        try {
            const extendedContent = await this.progressService.executeWithProgress(
                () => this.chatService.extendLyricSection(this.activeSection!.content, 4),
                this.translate.instant('lyricCreation.sectionEditor.extending'),
                this.translate.instant('lyricCreation.sectionEditor.extendingHint')
            );
            this.activeSection.content = this.removeQuotes(extendedContent);
        } catch (error: any) {
            this.notificationService.error(`Error extending section: ${error.message}`);
        } finally {
            this.isExtendingSection = false;
        }
    }

    rebuildFromLyricText(): void {
        const lyrics = this.lyricForm.get('lyrics')?.value || '';
        if (!lyrics.trim()) {
            this.notificationService.error(this.translate.instant('lyricCreation.errors.lyricsRequired'));
            return;
        }

        // Parse existing lyrics
        const sections = this.parseLyrics(lyrics);

        if (sections.length === 0) {
            this.notificationService.error(this.translate.instant('lyricCreation.rebuildFailed'));
            return;
        }

        // Confirm before overwriting architecture
        const confirmed = confirm(this.translate.instant('lyricCreation.confirmRebuild'));
        if (!confirmed) {
            return;
        }

        // Map parsed sections to SongSection enum
        const architectureSections: SongSectionItem[] = [];
        let hasWarnings = false;

        for (const section of sections) {
            const mapped = this.mapLabelToSongSection(section.label);

            if (!mapped) {
                // Unknown section type - log warning but continue
                console.warn(`Unknown section label: ${section.label} - skipping`);
                hasWarnings = true;
                continue;
            }

            architectureSections.push(mapped);
        }

        if (architectureSections.length === 0) {
            this.notificationService.error(this.translate.instant('lyricCreation.rebuildFailed'));
            return;
        }

        // Update architecture service
        this.architectureService.saveConfig({
            sections: architectureSections,
            lastModified: new Date()
        });

        // Show success notification
        if (hasWarnings) {
            this.notificationService.success(
                this.translate.instant('lyricCreation.rebuildSuccessWithWarnings', {count: architectureSections.length})
            );
        } else {
            this.notificationService.success(
                this.translate.instant('lyricCreation.rebuildSuccess', {count: architectureSections.length})
            );
        }
    }

    private mapLabelToSongSection(label: string): SongSectionItem | null {
        // Normalize label: lowercase and remove spaces/hyphens/underscores
        const normalized = label.toLowerCase().replace(/[\s_-]/g, '');

        // Extract base type and number (e.g., "verse1" -> "verse", "1")
        const match = normalized.match(/^([a-z]+)(\d*)$/);
        if (!match) {
            return null;
        }

        const [, baseType, number] = match;
        let section: SongSection | null = null;
        let displayName: string;

        // Map to SongSection enum
        switch (baseType) {
            case 'intro':
                section = SongSection.INTRO;
                displayName = 'INTRO';
                break;
            case 'verse':
                section = SongSection.VERSE;
                displayName = number ? `VERSE${number}` : 'VERSE1';
                break;
            case 'prechorus':
                section = SongSection.PRE_CHORUS;
                displayName = 'PRE_CHORUS';
                break;
            case 'chorus':
                section = SongSection.CHORUS;
                displayName = number ? `CHORUS${number}` : 'CHORUS';
                break;
            case 'bridge':
                section = SongSection.BRIDGE;
                displayName = number ? `BRIDGE${number}` : 'BRIDGE';
                break;
            case 'outro':
                section = SongSection.OUTRO;
                displayName = 'OUTRO';
                break;
            case 'postchorus':
                // POST_CHORUS is not in the enum - log warning
                console.warn('POST_CHORUS detected but not supported in architecture - skipping');
                return null;
            default:
                return null;
        }

        return {
            id: this.generateSectionId(),
            section,
            displayName
        };
    }

    private generateSectionId(): string {
        return `section_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    @HostListener('document:click', ['$event'])
    onDocumentClick(event: Event) {
        const target = event.target as HTMLElement;
        const dropdown = target.closest('.text-tools-dropdown-container');

        if (!dropdown && this.showTextToolsDropdown) {
            this.closeTextToolsDropdown();
        }
    }
}
