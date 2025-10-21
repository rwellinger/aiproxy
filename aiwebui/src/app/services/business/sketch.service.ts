import {Injectable, inject} from '@angular/core';
import {HttpClient} from '@angular/common/http';
import {Observable} from 'rxjs';
import {ApiConfigService} from '../config/api-config.service';

/**
 * Song Sketch model interface
 */
export interface Sketch {
  id: string;
  title?: string;
  lyrics?: string;
  prompt: string;
  tags?: string;
  workflow: 'draft' | 'used' | 'archived';
  created_at: string;
  updated_at?: string;
}

/**
 * Sketch list response from API
 */
export interface SketchListResponse {
  data: Sketch[];
  pagination: {
    total: number;
    limit: number;
    offset: number;
    has_more: boolean;
  };
}

/**
 * Sketch detail response from API
 */
export interface SketchDetailResponse {
  data: Sketch;
  success: boolean;
  message?: string;
}

/**
 * Service for managing song sketches
 */
@Injectable({
  providedIn: 'root'
})
export class SketchService {
  private http = inject(HttpClient);
  private apiConfig = inject(ApiConfigService);

  /**
   * Create a new sketch
   */
  createSketch(data: Partial<Sketch>): Observable<SketchDetailResponse> {
    return this.http.post<SketchDetailResponse>(
      this.apiConfig.endpoints.sketch.create(),
      data
    );
  }

  /**
   * Get list of sketches with optional filters
   */
  getSketches(
    limit = 20,
    offset = 0,
    workflow?: string,
    search?: string
  ): Observable<SketchListResponse> {
    return this.http.get<SketchListResponse>(
      this.apiConfig.endpoints.sketch.list(limit, offset, workflow, search)
    );
  }

  /**
   * Get single sketch by ID
   */
  getSketchById(id: string): Observable<SketchDetailResponse> {
    return this.http.get<SketchDetailResponse>(
      this.apiConfig.endpoints.sketch.detail(id)
    );
  }

  /**
   * Update an existing sketch
   */
  updateSketch(id: string, data: Partial<Sketch>): Observable<SketchDetailResponse> {
    return this.http.put<SketchDetailResponse>(
      this.apiConfig.endpoints.sketch.update(id),
      data
    );
  }

  /**
   * Delete a sketch
   */
  deleteSketch(id: string): Observable<{success: boolean; message?: string}> {
    return this.http.delete<{success: boolean; message?: string}>(
      this.apiConfig.endpoints.sketch.delete(id)
    );
  }
}
