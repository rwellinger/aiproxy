/**
 * Song Project Models - TypeScript interfaces and enums for song project management.
 */

export interface SongProject {
  id: string;
  user_id: string;
  project_name: string;
  s3_prefix: string;
  tags: string[];
  description?: string;
  project_status: 'new' | 'progress' | 'archived';
  created_at: string; // ISO format
  updated_at: string; // ISO format
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
  relative_path: string; // Full path with subdirectories (e.g., "Audio Files/Drums/Kick.wav")
  s3_key: string;
  file_size_bytes: number;
  file_hash?: string;
  is_synced: boolean;
  download_url?: string;
  created_at: string; // ISO format
  updated_at: string; // ISO format
}

export interface AssignedSong {
  id: string;
  title: string | null;
  workflow: string;
  file_type?: string | null;
  file_size_bytes?: number | null;
  created_at: string | null;
}

export interface AssignedSketch {
  id: string;
  title: string | null;
  prompt: string;
  workflow: string;
  created_at: string | null;
}

export interface AssignedImage {
  id: string;
  title: string | null;
  prompt: string | null;
  composition: string | null;
  width?: number | null;
  height?: number | null;
  created_at: string | null;
}

export interface ProjectFolderWithFiles extends ProjectFolder {
  files: ProjectFile[];
}

export interface ProjectFolderWithAssets extends ProjectFolderWithFiles {
  assigned_songs?: AssignedSong[];
  assigned_sketches?: AssignedSketch[];
  assigned_images?: AssignedImage[];
}

export interface SongProjectDetail extends SongProject {
  total_files: number;  // Live calculated
  total_size_bytes: number;  // Live calculated
  folders: ProjectFolderWithAssets[];
}

export interface SongProjectListItem {
  id: string;
  project_name: string;
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
  description?: string;
}

export interface SongProjectUpdateRequest {
  project_name?: string;
  tags?: string[];
  description?: string;
  cover_image_id?: string;
  project_status?: 'new' | 'progress' | 'archived';
}

export interface FileUploadRequest {
  file: File;
  folder_id: string;
}
