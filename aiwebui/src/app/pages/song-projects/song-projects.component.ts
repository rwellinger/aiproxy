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
import { MatMenuModule } from '@angular/material/menu';

import { SongProjectService } from '../../services/business/song-project.service';
import { NotificationService } from '../../services/ui/notification.service';
import { CreateProjectDialogComponent } from '../../dialogs/create-project-dialog/create-project-dialog.component';
import {
  SongProjectDetail,
  SongProjectListItem
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
    MatTooltipModule,
    MatMenuModule
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

  // Edit state
  isEditingProjectName = false;
  editProjectNameValue = '';

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

      // Sort folders numerically by folder_name (e.g., "01 Arrangement", "02 AI", ...)
      if (this.selectedProject?.folders) {
        this.selectedProject.folders.sort((a, b) =>
          a.folder_name.localeCompare(b.folder_name, undefined, { numeric: true })
        );
      }
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

      // Sort folders numerically by folder_name (e.g., "01 Arrangement", "02 AI", ...)
      if (this.selectedProject?.folders) {
        this.selectedProject.folders.sort((a, b) =>
          a.folder_name.localeCompare(b.folder_name, undefined, { numeric: true })
        );
      }
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
   * Refresh current project details.
   */
  async refreshProject(): Promise<void> {
    if (!this.selectedProject) return;

    try {
      this.isLoadingDetail = true;
      await this.selectProject(this.selectedProject);
      this.notificationService.success(
        this.translate.instant('common.refreshSuccess')
      );
    } catch (error) {
      console.error('Failed to refresh project:', error);
      this.notificationService.error(
        this.translate.instant('songProjects.messages.loadError')
      );
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
   * Get file path relative to folder (strips folder name prefix).
   * Example: "01 Arrangement/Media/drums.wav" → "Media/drums.wav"
   *
   * @param relativePath Full relative path (e.g., "01 Arrangement/Media/drums.wav")
   * @param folderName Folder name (e.g., "01 Arrangement")
   * @returns Path within folder (e.g., "Media/drums.wav")
   */
  getFilePathInFolder(relativePath: string, folderName: string): string {
    // Remove folder name prefix if present
    const prefix = folderName + '/';
    if (relativePath.startsWith(prefix)) {
      return relativePath.substring(prefix.length);
    }
    // Fallback: return full path if prefix doesn't match
    return relativePath;
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
   * Copy CLI upload command to clipboard.
   */
  async copyCLICommand(folder: any): Promise<void> {
    if (!this.selectedProject) return;

    const command = `aiproxy-cli upload ${this.selectedProject.id} ${folder.id}`;

    try {
      await navigator.clipboard.writeText(command);
      this.notificationService.success(
        this.translate.instant('songProjects.messages.cliUploadCommandCopied')
      );
    } catch (error) {
      console.error('Failed to copy to clipboard:', error);
      this.notificationService.error(
        this.translate.instant('songProjects.messages.clipboardError')
      );
    }
  }

  /**
   * Copy CLI download command to clipboard.
   */
  async copyCLIDownloadCommand(folder: any): Promise<void> {
    if (!this.selectedProject) return;

    const command = `aiproxy-cli download ${this.selectedProject.id} ${folder.id}`;

    try {
      await navigator.clipboard.writeText(command);
      this.notificationService.success(
        this.translate.instant('songProjects.messages.cliDownloadCommandCopied')
      );
    } catch (error) {
      console.error('Clipboard copy failed:', error);
      this.notificationService.error(
        this.translate.instant('songProjects.messages.cliCommandCopyFailed')
      );
    }
  }

  /**
   * Copy CLI mirror command to clipboard.
   */
  async copyCLIMirrorCommand(folder: any): Promise<void> {
    if (!this.selectedProject) return;

    const command = `aiproxy-cli mirror ${this.selectedProject.id} ${folder.id} . --dry-run`;

    try {
      await navigator.clipboard.writeText(command);
      this.notificationService.success(
        this.translate.instant('songProjects.messages.cliMirrorCommandCopied')
      );
    } catch (error) {
      console.error('Clipboard copy failed:', error);
      this.notificationService.error(
        this.translate.instant('songProjects.messages.cliCommandCopyFailed')
      );
    }
  }

  /**
   * Copy CLI clone command to clipboard (complete clone).
   */
  async copyCLICompleteCloneCommand(): Promise<void> {
    if (!this.selectedProject) return;

    const command = `aiproxy-cli clone ${this.selectedProject.id} .`;

    try {
      await navigator.clipboard.writeText(command);
      this.notificationService.success(
        this.translate.instant('songProjects.messages.cliCompleteCloneCommandCopied')
      );
    } catch (error) {
      console.error('Clipboard copy failed:', error);
      this.notificationService.error(
        this.translate.instant('songProjects.messages.cliCommandCopyFailed')
      );
    }
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

  /**
   * Navigate to Song View with song ID in state.
   */
  openSong(songId: string): void {
    this.router.navigate(['/songview'], {
      state: { selectedSongId: songId }
    });
  }

  /**
   * Navigate to Sketch Library with sketch ID in state.
   */
  openSketch(sketchId: string): void {
    this.router.navigate(['/song-sketch-library'], {
      state: { selectedSketchId: sketchId }
    });
  }

  /**
   * Navigate to Image View with image ID in state.
   */
  openImage(imageId: string): void {
    this.router.navigate(['/imageview'], {
      state: { selectedImageId: imageId }
    });
  }

  /**
   * Get smart folder content label (e.g., "2 images", "3 assets, 1 file").
   */
  getFolderContentLabel(folder: any): string {
    const fileCount = folder.files?.length || 0;
    const songCount = folder.assigned_songs?.length || 0;
    const sketchCount = folder.assigned_sketches?.length || 0;
    const imageCount = folder.assigned_images?.length || 0;
    const totalAssets = songCount + sketchCount + imageCount;

    // Only images (specific type)
    if (totalAssets > 0 && fileCount === 0 && songCount === 0 && sketchCount === 0 && imageCount > 0) {
      return this.translate.instant('songProjects.detail.folderContent.images', { count: imageCount });
    }

    // Only songs (specific type)
    if (totalAssets > 0 && fileCount === 0 && songCount > 0 && sketchCount === 0 && imageCount === 0) {
      return this.translate.instant('songProjects.detail.folderContent.songs', { count: songCount });
    }

    // Only sketches (specific type)
    if (totalAssets > 0 && fileCount === 0 && songCount === 0 && sketchCount > 0 && imageCount === 0) {
      return this.translate.instant('songProjects.detail.folderContent.sketches', { count: sketchCount });
    }

    // Mixed assets only
    if (totalAssets > 0 && fileCount === 0) {
      return this.translate.instant('songProjects.detail.folderContent.assets', { count: totalAssets });
    }

    // Assets + files
    if (totalAssets > 0 && fileCount > 0) {
      return this.translate.instant('songProjects.detail.folderContent.assetsAndFiles', {
        assetCount: totalAssets,
        fileCount: fileCount
      });
    }

    // Only files
    if (fileCount > 0) {
      return this.translate.instant('songProjects.detail.folderContent.files', { count: fileCount });
    }

    // Empty
    return this.translate.instant('songProjects.detail.folderContent.empty');
  }

  /**
   * Start editing project name.
   */
  startEditProjectName(): void {
    if (!this.selectedProject) return;
    this.editProjectNameValue = this.selectedProject.project_name;
    this.isEditingProjectName = true;
  }

  /**
   * Cancel editing project name.
   */
  cancelEditProjectName(): void {
    this.isEditingProjectName = false;
    this.editProjectNameValue = '';
  }

  /**
   * Save edited project name.
   */
  async saveProjectName(): Promise<void> {
    if (!this.selectedProject || !this.editProjectNameValue.trim()) {
      this.cancelEditProjectName();
      return;
    }

    const newName = this.editProjectNameValue.trim();
    if (newName === this.selectedProject.project_name) {
      this.cancelEditProjectName();
      return;
    }

    try {
      await firstValueFrom(
        this.projectService.updateProject(this.selectedProject.id, {
          project_name: newName
        })
      );

      this.notificationService.success(
        this.translate.instant('songProjects.messages.updateSuccess')
      );

      // Update local state
      this.selectedProject.project_name = newName;

      // Update in list
      const projectInList = this.projectList.find(p => p.id === this.selectedProject!.id);
      if (projectInList) {
        projectInList.project_name = newName;
      }

      this.cancelEditProjectName();
    } catch (error) {
      console.error('Failed to update project name:', error);
      this.notificationService.error(
        this.translate.instant('songProjects.messages.saveError')
      );
    }
  }
}
