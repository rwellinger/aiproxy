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
import { MatSelectModule } from '@angular/material/select';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatDialogModule, MatDialog } from '@angular/material/dialog';

import { EquipmentService } from '../../services/business/equipment.service';
import { NotificationService } from '../../services/ui/notification.service';
import { Equipment, EquipmentType, EquipmentStatus } from '../../models/equipment.model';

@Component({
  selector: 'app-equipment-gallery',
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
    MatSelectModule,
    MatProgressSpinnerModule,
    MatDialogModule
  ],
  templateUrl: './equipment-gallery.component.html',
  styleUrl: './equipment-gallery.component.scss'
})
export class EquipmentGalleryComponent implements OnInit, OnDestroy {
  // Equipment list and pagination
  equipmentList: Equipment[] = [];
  selectedEquipment: Equipment | null = null;
  pagination = {
    total: 0,
    limit: 8,
    offset: 0,
    has_more: false
  };

  // Search and filter
  searchTerm = '';
  selectedType: EquipmentType | 'all' = 'all';
  selectedStatus: EquipmentStatus | 'all' = 'all';

  // UI state
  isLoading = false;
  showDeleteConfirm = false;
  deleteEquipmentId: string | null = null;

  // Enums for template
  EquipmentType = EquipmentType;
  EquipmentStatus = EquipmentStatus;

  // RxJS subjects
  private searchSubject = new Subject<string>();
  private destroy$ = new Subject<void>();

  private equipmentService = inject(EquipmentService);
  private notificationService = inject(NotificationService);
  private translate = inject(TranslateService);
  private router = inject(Router);
  private dialog = inject(MatDialog);

  constructor() {
    // Setup search debouncing
    this.searchSubject.pipe(
      debounceTime(300),
      distinctUntilChanged(),
      takeUntil(this.destroy$)
    ).subscribe(searchTerm => {
      this.searchTerm = searchTerm;
      this.pagination.offset = 0;
      this.loadEquipment();
    });
  }

  ngOnInit(): void {
    this.loadEquipment();
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  /**
   * Load equipment list with current filters and pagination.
   */
  async loadEquipment(): Promise<void> {
    this.isLoading = true;

    try {
      const typeFilter = this.selectedType === 'all' ? undefined : this.selectedType;
      const statusFilter = this.selectedStatus === 'all' ? undefined : this.selectedStatus;
      const searchQuery = this.searchTerm.trim() || undefined;

      const response = await firstValueFrom(
        this.equipmentService.getEquipments(
          this.pagination.limit,
          this.pagination.offset,
          typeFilter,
          statusFilter,
          searchQuery
        )
      );

      this.equipmentList = response.data as Equipment[];
      this.pagination.total = response.pagination.total;
      this.pagination.has_more = response.pagination.has_more;
    } catch (error) {
      console.error('Failed to load equipment:', error);
      this.notificationService.error(
        this.translate.instant('equipment.messages.loadError')
      );
    } finally {
      this.isLoading = false;
    }
  }

  /**
   * Handle search input change.
   */
  onSearchChange(searchTerm: string): void {
    this.searchSubject.next(searchTerm);
  }

  /**
   * Handle type filter change.
   */
  onTypeFilterChange(): void {
    this.pagination.offset = 0;
    this.loadEquipment();
  }

  /**
   * Handle status filter change.
   */
  onStatusFilterChange(): void {
    this.pagination.offset = 0;
    this.loadEquipment();
  }

  /**
   * Select equipment to show details.
   */
  selectEquipment(equipment: Equipment): void {
    this.selectedEquipment = equipment;
  }

  /**
   * Navigate to equipment editor (edit mode).
   */
  editEquipment(id: string): void {
    this.router.navigate(['/equipment-editor', id]);
  }

  /**
   * Navigate to equipment editor (create mode).
   */
  createNew(): void {
    this.router.navigate(['/equipment-editor']);
  }

  /**
   * Show delete confirmation dialog.
   */
  confirmDelete(id: string, event: Event): void {
    event.stopPropagation();
    this.showDeleteConfirm = true;
    this.deleteEquipmentId = id;
  }

  /**
   * Delete equipment after confirmation.
   */
  async deleteEquipment(): Promise<void> {
    if (!this.deleteEquipmentId) return;

    try {
      await firstValueFrom(
        this.equipmentService.deleteEquipment(this.deleteEquipmentId)
      );

      this.notificationService.success(
        this.translate.instant('equipment.messages.deleteSuccess')
      );

      // Reload list
      await this.loadEquipment();

      // Clear selection if deleted
      if (this.selectedEquipment?.id === this.deleteEquipmentId) {
        this.selectedEquipment = null;
      }
    } catch (error) {
      console.error('Failed to delete equipment:', error);
      this.notificationService.error(
        this.translate.instant('equipment.messages.deleteError')
      );
    } finally {
      this.showDeleteConfirm = false;
      this.deleteEquipmentId = null;
    }
  }

  /**
   * Cancel delete operation.
   */
  cancelDelete(): void {
    this.showDeleteConfirm = false;
    this.deleteEquipmentId = null;
  }

  /**
   * Load more equipment (pagination).
   */
  loadMore(): void {
    if (!this.pagination.has_more || this.isLoading) return;
    this.pagination.offset += this.pagination.limit;
    this.loadEquipment();
  }

  /**
   * Get icon for equipment type.
   */
  getTypeIcon(type: EquipmentType): string {
    switch (type) {
      case EquipmentType.SOFTWARE:
        return 'desktop_windows';
      case EquipmentType.PLUGIN:
        return 'extension';
      default:
        return 'device_unknown';
    }
  }

  /**
   * Get color for status chip.
   */
  getStatusColor(status: EquipmentStatus): string {
    switch (status) {
      case EquipmentStatus.ACTIVE:
        return 'primary';
      case EquipmentStatus.TRIAL:
        return 'accent';
      case EquipmentStatus.EXPIRED:
        return 'warn';
      case EquipmentStatus.ARCHIVED:
        return '';
      default:
        return '';
    }
  }
}
