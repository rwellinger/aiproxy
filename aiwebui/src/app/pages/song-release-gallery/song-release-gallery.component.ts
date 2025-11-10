import { Component, OnInit, OnDestroy, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { Subject, debounceTime, distinctUntilChanged, takeUntil } from 'rxjs';
import { TranslateModule, TranslateService } from '@ngx-translate/core';
import { MatCardModule } from '@angular/material/card';

import { SongReleaseService } from '../../services/business/song-release.service';
import { NotificationService } from '../../services/ui/notification.service';
import { SongRelease, SongReleaseListItem, ReleaseType, ReleaseStatus } from '../../models/song-release.model';

@Component({
  selector: 'app-song-release-gallery',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    TranslateModule,
    MatCardModule
  ],
  templateUrl: './song-release-gallery.component.html',
  styleUrl: './song-release-gallery.component.scss'
})
export class SongReleaseGalleryComponent implements OnInit, OnDestroy {
  // Release list and pagination
  releaseList: SongReleaseListItem[] = [];
  selectedRelease: SongRelease | null = null;
  currentPage = 0;
  pagination = {
    total: 0,
    limit: 8,
    offset: 0
  };

  // Search and filter
  searchTerm = '';
  selectedStatusFilter: string = 'all';

  // UI state
  isLoading = false;
  isLoadingDetail = false;

  // Enums for template
  ReleaseType = ReleaseType;
  ReleaseStatus = ReleaseStatus;

  // Math for template
  Math = Math;

  // RxJS subjects
  private searchSubject = new Subject<string>();
  private destroy$ = new Subject<void>();

  private releaseService = inject(SongReleaseService);
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
      this.loadReleases(0);
    });
  }

  ngOnInit(): void {
    this.loadReleases(0);
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  /**
   * Load releases with pagination and filters
   */
  async loadReleases(page: number): Promise<void> {
    this.isLoading = true;
    this.currentPage = page;
    this.pagination.offset = page * this.pagination.limit;

    try {
      const response = await this.releaseService.getReleases(
        this.pagination.limit,
        this.pagination.offset,
        this.selectedStatusFilter !== 'all' ? this.selectedStatusFilter : undefined,
        this.searchTerm || undefined
      ).toPromise();

      if (response) {
        this.releaseList = response.items || [];
        this.pagination.total = response.total || 0;
      } else {
        this.releaseList = [];
        this.pagination.total = 0;
      }
    } catch (error) {
      console.error('Failed to load releases:', error);
      this.releaseList = [];
      this.pagination.total = 0;
      this.notificationService.error(this.translate.instant('songRelease.messages.loadError'));
    } finally {
      this.isLoading = false;
    }
  }

  /**
   * Select release and load full details
   */
  async selectRelease(release: SongReleaseListItem): Promise<void> {
    this.isLoadingDetail = true;

    try {
      const response = await this.releaseService.getReleaseById(release.id).toPromise();
      if (response?.data) {
        this.selectedRelease = response.data;
      }
    } catch (error) {
      console.error('Failed to load release details:', error);
      this.notificationService.error(this.translate.instant('songRelease.messages.loadError'));
    } finally {
      this.isLoadingDetail = false;
    }
  }

  /**
   * Handle search input change
   */
  onSearchChange(value: string): void {
    this.searchSubject.next(value);
  }

  /**
   * Handle status filter change
   */
  selectStatusFilter(filter: string): void {
    this.selectedStatusFilter = filter;
    this.loadReleases(0);
  }

  /**
   * Navigate to specific page
   */
  changePage(page: number): void {
    if (page >= 0 && page < this.totalPages) {
      this.loadReleases(page);
    }
  }

  /**
   * Get total number of pages
   */
  get totalPages(): number {
    return Math.ceil(this.pagination.total / this.pagination.limit);
  }

  /**
   * Format date for display
   */
  formatDate(dateString?: string): string {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleDateString();
  }

  /**
   * Get status badge CSS class
   */
  getStatusClass(status: ReleaseStatus): string {
    const classMap: Record<ReleaseStatus, string> = {
      [ReleaseStatus.DRAFT]: 'badge-draft',
      [ReleaseStatus.ARRANGING]: 'badge-arranging',
      [ReleaseStatus.MIXING]: 'badge-mixing',
      [ReleaseStatus.MASTERING]: 'badge-mastering',
      [ReleaseStatus.REJECTED]: 'badge-rejected',
      [ReleaseStatus.UPLOADED]: 'badge-uploaded',
      [ReleaseStatus.RELEASED]: 'badge-released',
      [ReleaseStatus.DOWNTAKEN]: 'badge-downtaken',
      [ReleaseStatus.ARCHIVED]: 'badge-archived'
    };
    return classMap[status] || 'badge-draft';
  }

  /**
   * Copy text to clipboard
   */
  async copyToClipboard(text: string, messageKey: string): Promise<void> {
    try {
      await navigator.clipboard.writeText(text);
      this.notificationService.success(this.translate.instant(messageKey));
    } catch (error) {
      this.notificationService.error(this.translate.instant('songRelease.messages.copyError'));
    }
  }

  /**
   * Create new release (navigate to editor)
   */
  createNewRelease(): void {
    this.router.navigate(['/song-releases/new']);
  }

  /**
   * Edit selected release
   */
  editRelease(): void {
    if (!this.selectedRelease) return;
    this.router.navigate(['/song-releases/edit', this.selectedRelease.id]);
  }

  /**
   * Delete release
   */
  async deleteRelease(): Promise<void> {
    if (!this.selectedRelease) return;

    const confirmed = confirm(this.translate.instant('songRelease.messages.deleteConfirm'));
    if (!confirmed) return;

    try {
      await this.releaseService.deleteRelease(this.selectedRelease.id).toPromise();
      this.notificationService.success(this.translate.instant('songRelease.messages.deleteSuccess'));
      this.selectedRelease = null;
      this.loadReleases(this.currentPage);
    } catch (error) {
      console.error('Failed to delete release:', error);
      this.notificationService.error(this.translate.instant('songRelease.messages.deleteError'));
    }
  }
}
