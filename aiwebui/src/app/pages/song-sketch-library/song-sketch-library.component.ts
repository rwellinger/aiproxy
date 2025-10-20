import { Component, OnInit, ViewEncapsulation, OnDestroy, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { Subject, debounceTime, distinctUntilChanged, takeUntil, firstValueFrom } from 'rxjs';
import { TranslateModule, TranslateService } from '@ngx-translate/core';
import { MatCardModule } from '@angular/material/card';
import { MatSnackBarModule } from '@angular/material/snack-bar';

import { SketchService, Sketch } from '../../services/business/sketch.service';
import { NotificationService } from '../../services/ui/notification.service';

@Component({
  selector: 'app-song-sketch-library',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    TranslateModule,
    MatCardModule,
    MatSnackBarModule
  ],
  templateUrl: './song-sketch-library.component.html',
  styleUrl: './song-sketch-library.component.scss',
  encapsulation: ViewEncapsulation.None
})
export class SongSketchLibraryComponent implements OnInit, OnDestroy {
  // Sketches list and pagination
  sketches: Sketch[] = [];
  selectedSketch: Sketch | null = null;
  pagination = {
    total: 0,
    limit: 20,
    offset: 0,
    has_more: false
  };

  // Search and filter
  searchTerm = '';
  currentWorkflow: 'all' | 'draft' | 'used' | 'archived' = 'all';
  sortBy = 'created_at';
  sortDirection: 'asc' | 'desc' = 'desc';

  // UI state
  isLoading = false;
  showDeleteConfirm = false;
  deleteSketchId: string | null = null;

  // RxJS subjects
  private searchSubject = new Subject<string>();
  private destroy$ = new Subject<void>();

  private sketchService = inject(SketchService);
  private notificationService = inject(NotificationService);
  private translate = inject(TranslateService);
  private router = inject(Router);

  constructor() {
    // Setup search debouncing
    this.searchSubject.pipe(
      debounceTime(300),
      distinctUntilChanged(),
      takeUntil(this.destroy$)
    ).subscribe(searchTerm => {
      this.searchTerm = searchTerm;
      this.loadSketches();
    });
  }

  ngOnInit(): void {
    this.loadSketches();
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  async loadSketches(page = 0): Promise<void> {
    this.isLoading = true;
    try {
      const offset = page * this.pagination.limit;
      const workflowParam = this.currentWorkflow === 'all' ? undefined : this.currentWorkflow;

      const response = await firstValueFrom(
        this.sketchService.getSketches(
          this.pagination.limit,
          offset,
          workflowParam
        )
      );

      this.sketches = response.data || [];
      this.pagination = response.pagination || this.pagination;
      this.pagination.offset = offset;

      // Select first sketch if nothing selected
      if (this.sketches.length > 0 && !this.selectedSketch) {
        this.selectSketch(this.sketches[0]);
      } else if (this.sketches.length === 0) {
        this.selectedSketch = null;
      }
    } catch (error: any) {
      this.notificationService.error(
        this.translate.instant('songSketch.library.messages.loadingError') + ': ' + error.message
      );
    } finally {
      this.isLoading = false;
    }
  }

  selectSketch(sketch: Sketch): void {
    this.selectedSketch = sketch;
  }

  onSearchChange(searchTerm: string): void {
    this.searchSubject.next(searchTerm);
  }

  onWorkflowChange(workflow: 'all' | 'draft' | 'used' | 'archived'): void {
    this.currentWorkflow = workflow;
    this.pagination.offset = 0;
    this.loadSketches(0);
  }

  async changePage(page: number): Promise<void> {
    await this.loadSketches(page);
  }

  get currentPage(): number {
    return Math.floor(this.pagination.offset / this.pagination.limit);
  }

  get totalPages(): number {
    return Math.ceil(this.pagination.total / this.pagination.limit);
  }

  editSketch(): void {
    // Navigate to sketch creator and load the sketch data
    // For now, we'll just show a message
    this.notificationService.error(
      this.translate.instant('songSketch.library.messages.editNotImplemented')
    );
  }

  confirmDeleteSketch(sketchId: string): void {
    this.deleteSketchId = sketchId;
    this.showDeleteConfirm = true;
  }

  cancelDelete(): void {
    this.showDeleteConfirm = false;
    this.deleteSketchId = null;
  }

  async deleteSketch(): Promise<void> {
    if (!this.deleteSketchId) return;

    try {
      await firstValueFrom(
        this.sketchService.deleteSketch(this.deleteSketchId)
      );

      this.notificationService.success(
        this.translate.instant('songSketch.library.messages.deleted')
      );

      // Clear selection if deleted sketch was selected
      if (this.selectedSketch?.id === this.deleteSketchId) {
        this.selectedSketch = null;
      }

      // Reload list
      await this.loadSketches(this.currentPage);
    } catch (error: any) {
      this.notificationService.error(
        this.translate.instant('songSketch.library.messages.deleteError') + ': ' + error.message
      );
    } finally {
      this.cancelDelete();
    }
  }

  async archiveSketch(sketch: Sketch): Promise<void> {
    try {
      await firstValueFrom(
        this.sketchService.updateSketch(sketch.id, {
          workflow: 'archived'
        })
      );

      this.notificationService.success(
        this.translate.instant('songSketch.library.messages.archived')
      );

      // Reload list
      await this.loadSketches(this.currentPage);
    } catch (error: any) {
      this.notificationService.error(
        this.translate.instant('songSketch.library.messages.archiveError') + ': ' + error.message
      );
    }
  }

  navigateToSketchCreator(): void {
    this.router.navigate(['/song-sketch-creator']);
  }

  formatDate(dateString: string): string {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  }

  getWorkflowLabel(workflow: string): string {
    return this.translate.instant(`songSketch.workflow.${workflow}`);
  }

  getWorkflowClass(workflow: string): string {
    const classMap: Record<string, string> = {
      draft: 'badge-draft',
      used: 'badge-used',
      archived: 'badge-archived'
    };
    return classMap[workflow] || 'badge-draft';
  }
}
