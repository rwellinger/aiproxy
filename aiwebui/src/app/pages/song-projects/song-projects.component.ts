import { Component, OnInit, OnDestroy, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { Subject, debounceTime, distinctUntilChanged, takeUntil, firstValueFrom } from 'rxjs';
import { TranslateModule, TranslateService } from '@ngx-translate/core';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatChipsModule } from '@angular/material/chips';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatExpansionModule } from '@angular/material/expansion';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { MatTooltipModule } from '@angular/material/tooltip';

import { SongProjectService } from '../../services/business/song-project.service';
import { NotificationService } from '../../services/ui/notification.service';
import { CreateProjectDialogComponent } from '../../dialogs/create-project-dialog/create-project-dialog.component';
import {
  SongProjectDetail,
  SongProjectListItem,
  SyncStatus
} from '../../models/song-project.model';

@Component({
  selector: 'app-song-projects',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    TranslateModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatChipsModule,
    MatFormFieldModule,
    MatInputModule,
    MatProgressSpinnerModule,
    MatExpansionModule,
    MatDialogModule,
    MatTooltipModule
  ],
  templateUrl: './song-projects.component.html',
  styleUrl: './song-projects.component.scss'
})
export class SongProjectsComponent implements OnInit, OnDestroy {
  // Project list and pagination
  projectList: SongProjectListItem[] = [];
  selectedProject: SongProjectDetail | null = null;
  totalProjects = 0;
  pagination = {
    total: 0,
    limit: 20,
    offset: 0,
    has_more: false
  };

  // Search and filter
  searchTerm = '';

  // UI state
  isLoading = false;
  isLoadingDetail = false;

  // Enums for template
  SyncStatus = SyncStatus;

  // Math for template
  Math = Math;

  // RxJS subjects
  private searchSubject = new Subject<string>();
  private destroy$ = new Subject<void>();

  private projectService = inject(SongProjectService);
  private notificationService = inject(NotificationService);
  private translate = inject(TranslateService);
  private router = inject(Router);
  private dialog = inject(MatDialog);

  // Navigation state (must be captured in constructor)
  private navigationState: any = null;

  constructor() {
    // IMPORTANT: getCurrentNavigation() must be called in constructor!
    const navigation = this.router.getCurrentNavigation();
    this.navigationState = navigation?.extras?.state;
  }

  ngOnInit(): void {
    // Setup search debounce
    this.searchSubject
      .pipe(
        debounceTime(300),
        distinctUntilChanged(),
        takeUntil(this.destroy$)
      )
      .subscribe(searchTerm => {
        this.searchTerm = searchTerm;
        this.pagination.offset = 0;
        this.loadProjects();
      });

    // Load initial data and auto-select project if provided via state
    this.loadProjects().then(() => {
      const selectedProjectId = this.navigationState?.['selectedProjectId'];
      if (selectedProjectId) {
        this.selectProjectById(selectedProjectId);
      } else if (this.projectList.length > 0 && !this.selectedProject) {
        // Auto-select first project if no navigation state
        this.selectProject(this.projectList[0]);
      }
    });
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  /**
   * Load projects list from API.
   */
  async loadProjects(): Promise<void> {
    this.isLoading = true;

    try {
      const response = await firstValueFrom(
        this.projectService.getProjects(
          this.pagination.limit,
          this.pagination.offset,
          this.searchTerm || undefined
        )
      );

      this.projectList = response.data;
      this.pagination = response.pagination;
      this.totalProjects = response.pagination.total;
    } catch (error) {
      console.error('Failed to load projects:', error);
      this.notificationService.error(
        this.translate.instant('songProjects.messages.loadError')
      );
    } finally {
      this.isLoading = false;
    }
  }

  /**
   * Select a project and load details.
   */
  async selectProject(project: SongProjectListItem): Promise<void> {
    this.isLoadingDetail = true;

    try {
      const response = await firstValueFrom(
        this.projectService.getProjectById(project.id)
      );

      this.selectedProject = response.data;
    } catch (error) {
      console.error('Failed to load project details:', error);
      this.notificationService.error(
        this.translate.instant('songProjects.messages.loadError')
      );
    } finally {
      this.isLoadingDetail = false;
    }
  }

  /**
   * Select a project by ID (for auto-selection from router state).
   */
  async selectProjectById(projectId: string): Promise<void> {
    this.isLoadingDetail = true;

    try {
      const response = await firstValueFrom(
        this.projectService.getProjectById(projectId)
      );

      this.selectedProject = response.data;
    } catch (error) {
      console.error('Failed to load project details:', error);
      this.notificationService.error(
        this.translate.instant('songProjects.messages.loadError')
      );
    } finally {
      this.isLoadingDetail = false;
    }
  }

  /**
   * Delete project with confirmation.
   */
  async deleteProject(): Promise<void> {
    if (!this.selectedProject) return;

    const confirmed = confirm(
      this.translate.instant('songProjects.messages.deleteConfirm')
    );

    if (!confirmed) return;

    try {
      await firstValueFrom(
        this.projectService.deleteProject(this.selectedProject.id)
      );

      this.notificationService.success(
        this.translate.instant('songProjects.messages.deleteSuccess')
      );

      // Reset selection and reload list
      this.selectedProject = null;
      await this.loadProjects();
    } catch (error) {
      console.error('Failed to delete project:', error);
      this.notificationService.error(
        this.translate.instant('songProjects.messages.deleteError')
      );
    }
  }

  /**
   * Handle search input.
   */
  onSearchChange(searchTerm: string): void {
    this.searchSubject.next(searchTerm);
  }

  /**
   * Load more projects (pagination).
   */
  loadMore(): void {
    if (this.pagination.has_more && !this.isLoading) {
      this.pagination.offset += this.pagination.limit;
      this.loadProjects();
    }
  }

  /**
   * Format file size to human-readable string.
   */
  formatFileSize(bytes: number): string {
    if (bytes === 0) return '0 Bytes';

    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));

    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
  }

  /**
   * Get sync status badge class.
   */
  getSyncStatusClass(status: SyncStatus): string {
    const statusMap: Record<SyncStatus, string> = {
      [SyncStatus.LOCAL]: 'status-local',
      [SyncStatus.CLOUD]: 'status-cloud',
      [SyncStatus.SYNCED]: 'status-synced',
      [SyncStatus.SYNCING]: 'status-syncing'
    };

    return statusMap[status] || 'status-local';
  }

  /**
   * Download file (opens pre-signed URL).
   */
  downloadFile(downloadUrl: string): void {
    if (downloadUrl) {
      window.open(downloadUrl, '_blank');
    }
  }

  /**
   * Upload file to project folder.
   */
  async uploadFile(folder: any): Promise<void> {
    // Create hidden file input
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '*';

    input.onchange = async (e: any) => {
      const file = e.target.files[0];
      if (!file) return;

      // Validate file size (500MB max)
      const maxSizeBytes = 500 * 1024 * 1024; // 500MB
      if (file.size > maxSizeBytes) {
        this.notificationService.error(
          this.translate.instant('songProjects.messages.fileTooLarge', { size: '500MB' })
        );
        return;
      }

      // Create FormData
      const formData = new FormData();
      formData.append('file', file);
      formData.append('folder_id', folder.id);

      try {
        await firstValueFrom(
          this.projectService.uploadFile(this.selectedProject!.id, formData)
        );

        this.notificationService.success(
          this.translate.instant('songProjects.messages.uploadSuccess')
        );

        // Reload project details to show new file
        if (this.selectedProject) {
          await this.selectProject(this.selectedProject);
        }
      } catch (error) {
        console.error('Upload failed:', error);
        this.notificationService.error(
          this.translate.instant('songProjects.messages.uploadError')
        );
      }
    };

    // Trigger file selection dialog
    input.click();
  }

  /**
   * Open dialog to create new project.
   */
  createNewProject(): void {
    const dialogRef = this.dialog.open(CreateProjectDialogComponent, {
      width: '600px',
      minHeight: '400px',
      disableClose: false
    });

    dialogRef.afterClosed().subscribe(async (result) => {
      if (!result) {
        return; // User cancelled
      }

      try {
        await firstValueFrom(
          this.projectService.createProject(result)
        );

        this.notificationService.success(
          this.translate.instant('songProjects.messages.createSuccess')
        );

        // Reload projects list
        await this.loadProjects();
      } catch (error) {
        console.error('Failed to create project:', error);
        this.notificationService.error(
          this.translate.instant('songProjects.messages.saveError')
        );
      }
    });
  }
}
