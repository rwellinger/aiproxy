/**
 * Song Project Models - TypeScript interfaces and enums for song project management.
 */

export enum SyncStatus {
  LOCAL = 'local',
  CLOUD = 'cloud',
  SYNCED = 'synced',
  SYNCING = 'syncing'
}

export enum StorageBackend {
  S3 = 's3',
  LOCAL = 'local'
}

export interface SongProject {
  id: string;
  user_id: string;
  project_name: string;
  s3_prefix: string;
  sync_status: SyncStatus;
  tags: string[];
  total_files: number;
  total_size_bytes: number;
  created_at: string; // ISO format
  updated_at: string; // ISO format
  last_sync_at?: string; // ISO format
}

export interface ProjectFolder {
  id: string;
  project_id: string;
  folder_name: string;
  folder_type: string;
  s3_prefix: string;
  custom_icon?: string;
  created_at: string; // ISO format
}

export interface ProjectFile {
  id: string;
  project_id: string;
  folder_id: string;
  filename: string;
  s3_key: string;
  file_size_bytes: number;
  file_hash?: string;
  storage_backend: StorageBackend;
  is_synced: boolean;
  download_url?: string;
  created_at: string; // ISO format
  updated_at: string; // ISO format
}

export interface ProjectFolderWithFiles extends ProjectFolder {
  files: ProjectFile[];
}

export interface SongProjectDetail extends SongProject {
  folders: ProjectFolderWithFiles[];
}

export interface SongProjectListItem {
  id: string;
  project_name: string;
  sync_status: SyncStatus;
  tags: string[];
  total_files: number;
  total_size_bytes: number;
  created_at: string;
  updated_at: string;
}

export interface SongProjectListResponse {
  data: SongProjectListItem[];
  pagination: {
    total: number;
    limit: number;
    offset: number;
    has_more: boolean;
  };
}

export interface SongProjectDetailResponse {
  data: SongProjectDetail;
  message?: string;
}

export interface SongProjectCreateRequest {
  project_name: string;
  tags?: string[];
}

export interface SongProjectUpdateRequest {
  project_name?: string;
  tags?: string[];
  sync_status?: SyncStatus;
}

export interface FileUploadRequest {
  file: File;
  folder_id: string;
}
