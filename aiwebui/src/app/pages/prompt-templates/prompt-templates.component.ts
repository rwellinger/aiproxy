import {Component, OnInit, OnDestroy, ViewChild, ElementRef, inject} from '@angular/core';
import {CommonModule} from '@angular/common';
import {FormsModule} from '@angular/forms';
import {Subject, debounceTime, distinctUntilChanged, takeUntil} from 'rxjs';
import {PromptTemplate, PromptTemplateUpdate} from '../../models/prompt-template.model';
import {PromptTemplateService} from '../../services/config/prompt-template.service';
import {NotificationService} from '../../services/ui/notification.service';
import {UserSettingsService} from '../../services/user-settings.service';
import {MatSnackBarModule} from '@angular/material/snack-bar';
import {MatCardModule} from '@angular/material/card';
import {MatButtonModule} from '@angular/material/button';
import {TranslateModule, TranslateService} from '@ngx-translate/core';

@Component({
    selector: 'app-prompt-templates',
    standalone: true,
    imports: [CommonModule, FormsModule, MatSnackBarModule, MatCardModule, MatButtonModule, TranslateModule],
    templateUrl: './prompt-templates.component.html',
    styleUrl: './prompt-templates.component.scss'
})
export class PromptTemplatesComponent implements OnInit, OnDestroy {
    // Template data
    templates: PromptTemplate[] = [];
    filteredTemplates: PromptTemplate[] = [];
    paginatedTemplates: PromptTemplate[] = [];
    selectedTemplate: PromptTemplate | null = null;

    // Pagination
    pagination = {
        total: 0,
        limit: 8, // Will be overridden by user settings
        offset: 0
    };

    // UI state
    isLoading = false;
    loadingMessage = '';

    // Search functionality
    searchTerm: string = '';
    private searchSubject = new Subject<string>();
    private destroy$ = new Subject<void>();

    // Make Math available in template
    Math = Math;

    // Editing state
    editingTemplate: PromptTemplate | null = null;
    editForm = {
        pre_condition: '',
        post_condition: '',
        description: '',
        model: '',
        temperature: null as number | null,
        max_tokens: null as number | null
    };

    // Available models
    availableModels = [
        {value: 'llama3.2:3b', label: 'Llama 3.2 3B'},
        {value: 'gpt-oss:20b', label: 'GPT-OSS 20B'},
        {value: 'deepseek-r1:8b', label: 'DeepSeek R1 8B'},
        {value: 'gemma3:4b', label: 'Gemma 3 4B'}
    ];

    // Temperature options (0.0 to 2.0 in 0.1 steps)
    temperatureOptions = Array.from({length: 21}, (_, i) => {
        const value = (i * 0.1);
        return {value: Math.round(value * 10) / 10, label: value.toFixed(1)};
    });

    @ViewChild('searchInput') searchInput!: ElementRef;
    @ViewChild('preConditionTextarea') preConditionTextarea!: ElementRef;

    private promptService = inject(PromptTemplateService);
    private notificationService = inject(NotificationService);
    private settingsService = inject(UserSettingsService);
    private translate = inject(TranslateService);

    constructor() {
        // Setup search debouncing
        this.searchSubject.pipe(
            debounceTime(300),
            distinctUntilChanged(),
            takeUntil(this.destroy$)
        ).subscribe(searchTerm => {
            this.searchTerm = searchTerm;
            this.applyFilter();
            // Maintain focus on search input
            if (document.activeElement === this.searchInput?.nativeElement) {
                setTimeout(() => this.searchInput.nativeElement.focus(), 0);
            }
        });
    }

    ngOnInit(): void {
        this.loadUserSettings();
    }

    private loadUserSettings(): void {
        this.settingsService.getSettings()
            .pipe(takeUntil(this.destroy$))
            .subscribe(settings => {
                this.pagination.limit = settings.promptListLimit;
                this.loadTemplates();
            });
    }

    ngOnDestroy(): void {
        this.destroy$.next();
        this.destroy$.complete();
    }

    async loadTemplates(): Promise<void> {
        this.isLoading = true;
        this.loadingMessage = this.translate.instant('promptTemplates.notifications.loading');

        try {
            this.templates = await this.promptService.getAllTemplates().toPromise() || [];
            this.applyFilter();

            // Auto-select first template if available and none selected
            if (this.filteredTemplates.length > 0 && !this.selectedTemplate) {
                this.selectTemplate(this.filteredTemplates[0]);
            }
        } catch (error: any) {
            this.notificationService.error(this.translate.instant('promptTemplates.notifications.loadError', { message: error.message }));
            this.templates = [];
            this.filteredTemplates = [];
        } finally {
            this.isLoading = false;
        }
    }

    applyFilter(): void {
        if (!this.searchTerm.trim()) {
            this.filteredTemplates = [...this.templates];
        } else {
            const term = this.searchTerm.toLowerCase();
            this.filteredTemplates = this.templates.filter(template =>
                template.category.toLowerCase().includes(term) ||
                template.action.toLowerCase().includes(term)
            );
        }

        // Update pagination after filtering
        this.pagination.total = this.filteredTemplates.length;
        this.pagination.offset = 0; // Reset to first page
        this.updatePaginatedTemplates();
    }

    private updatePaginatedTemplates(): void {
        const start = this.pagination.offset;
        const end = start + this.pagination.limit;
        this.paginatedTemplates = this.filteredTemplates.slice(start, end);

        // Auto-select first template if available and none selected
        if (this.paginatedTemplates.length > 0 && !this.selectedTemplate) {
            this.selectTemplate(this.paginatedTemplates[0]);
        } else if (this.paginatedTemplates.length === 0) {
            this.selectedTemplate = null;
        }
    }

    onSearchChange(event: Event): void {
        const value = (event.target as HTMLInputElement).value;
        this.searchSubject.next(value);
    }

    clearSearch(): void {
        this.searchTerm = '';
        this.searchSubject.next('');
    }

    selectTemplate(template: PromptTemplate): void {
        this.selectedTemplate = template;
        this.cancelEdit(); // Clear any ongoing edits
    }

    startEdit(): void {
        if (!this.selectedTemplate) return;

        this.editingTemplate = {...this.selectedTemplate};
        this.editForm = {
            pre_condition: this.selectedTemplate.pre_condition,
            post_condition: this.selectedTemplate.post_condition,
            description: this.selectedTemplate.description || '',
            model: this.selectedTemplate.model || '',
            temperature: this.selectedTemplate.temperature || null,
            max_tokens: this.selectedTemplate.max_tokens || null
        };

        // Focus pre_condition textarea after view updates
        setTimeout(() => {
            if (this.preConditionTextarea) {
                this.preConditionTextarea.nativeElement.focus();
            }
        }, 100);
    }

    cancelEdit(): void {
        this.editingTemplate = null;
        this.editForm = {
            pre_condition: '',
            post_condition: '',
            description: '',
            model: '',
            temperature: null,
            max_tokens: null
        };
    }

    async saveTemplate(): Promise<void> {
        if (!this.selectedTemplate || !this.editingTemplate) return;

        this.isLoading = true;
        this.loadingMessage = this.translate.instant('promptTemplates.notifications.saving');

        try {
            const update: PromptTemplateUpdate = {
                pre_condition: this.editForm.pre_condition.trim(),
                post_condition: this.editForm.post_condition.trim(),
                description: this.editForm.description.trim(),
                model: this.editForm.model || undefined,
                temperature: this.editForm.temperature || undefined,
                max_tokens: this.editForm.max_tokens || undefined
            };

            const updatedTemplate = await this.promptService.updateTemplateAsync(
                this.selectedTemplate.category,
                this.selectedTemplate.action,
                update
            );

            // Update local data
            const templateIndex = this.templates.findIndex(t =>
                t.category === this.selectedTemplate!.category &&
                t.action === this.selectedTemplate!.action
            );

            if (templateIndex !== -1) {
                this.templates[templateIndex] = updatedTemplate;
                this.selectedTemplate = updatedTemplate;
            }

            this.applyFilter();
            this.cancelEdit();
        } catch (error: any) {
            this.notificationService.error(this.translate.instant('promptTemplates.notifications.saveError', { message: error.message }));
        } finally {
            this.isLoading = false;
        }
    }

    getTemplateDisplayName(template: PromptTemplate): string {
        return `${template.category} / ${template.action}`;
    }

    formatDate(dateString: string): string {
        try {
            return new Date(dateString).toLocaleDateString('de-CH', {
                day: '2-digit',
                month: '2-digit',
                year: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });
        } catch {
            return dateString;
        }
    }

    trackByTemplate(index: number, template: PromptTemplate): string {
        return `${template.category}-${template.action}`;
    }

    getTokensToWordsHint(tokens: number | null | undefined): string {
        if (!tokens || tokens === null || tokens === undefined) return '';
        // Rough estimation: 1 token ≈ 0.75 words
        const words = Math.round(tokens * 0.75);
        return this.translate.instant('promptTemplates.detail.tokensHint', { words });
    }

    // Pagination methods
    getVisiblePages(): (number | string)[] {
        const totalPages = Math.ceil(this.pagination.total / this.pagination.limit);
        const current = Math.floor(this.pagination.offset / this.pagination.limit) + 1;
        const pages: (number | string)[] = [];

        if (totalPages <= 7) {
            // Show all pages if 7 or less
            for (let i = 1; i <= totalPages; i++) {
                pages.push(i);
            }
        } else {
            // Smart pagination with ellipsis
            if (current <= 4) {
                // Show: 1 2 3 4 5 ... last
                for (let i = 1; i <= 5; i++) pages.push(i);
                pages.push('...');
                pages.push(totalPages);
            } else if (current >= totalPages - 3) {
                // Show: 1 ... n-4 n-3 n-2 n-1 n
                pages.push(1);
                pages.push('...');
                for (let i = totalPages - 4; i <= totalPages; i++) pages.push(i);
            } else {
                // Show: 1 ... current-1 current current+1 ... last
                pages.push(1);
                pages.push('...');
                for (let i = current - 1; i <= current + 1; i++) pages.push(i);
                pages.push('...');
                pages.push(totalPages);
            }
        }

        return pages;
    }

    goToPage(pageIndex: number): void {
        const totalPages = Math.ceil(this.pagination.total / this.pagination.limit);
        if (pageIndex >= 0 && pageIndex < totalPages) {
            this.pagination.offset = pageIndex * this.pagination.limit;
            this.updatePaginatedTemplates();
        }
    }

    nextPage(): void {
        const totalPages = Math.ceil(this.pagination.total / this.pagination.limit);
        const currentPage = Math.floor(this.pagination.offset / this.pagination.limit);
        if (currentPage < totalPages - 1) {
            this.goToPage(currentPage + 1);
        }
    }

    previousPage(): void {
        const currentPage = Math.floor(this.pagination.offset / this.pagination.limit);
        if (currentPage > 0) {
            this.goToPage(currentPage - 1);
        }
    }

    trackByPage(index: number, page: number | string): number | string {
        return page;
    }
}
