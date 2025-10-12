import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable, firstValueFrom } from 'rxjs';
import { OllamaModel, OpenAIModel } from '../../models/conversation.model';
import { ApiConfigService } from './api-config.service';

interface CacheEntry<T> {
  data: T;
  timestamp: number;
}

/**
 * Model Cache Service
 * Provides TTL-based caching for AI model lists (Ollama & OpenAI)
 * Prevents unnecessary API calls by caching model data
 */
@Injectable({
  providedIn: 'root'
})
export class ModelCacheService {
  private http = inject(HttpClient);
  private apiConfig = inject(ApiConfigService);

  // Cache TTL in milliseconds (default: 5 minutes)
  private readonly CACHE_TTL = 5 * 60 * 1000;

  // BehaviorSubjects for reactive model data
  private ollamaModels$ = new BehaviorSubject<OllamaModel[]>([]);
  private openaiModels$ = new BehaviorSubject<OpenAIModel[]>([]);

  // Cache entries
  private ollamaCache: CacheEntry<OllamaModel[]> | null = null;
  private openaiCache: CacheEntry<OpenAIModel[]> | null = null;

  // Loading states
  private isLoadingOllama = false;
  private isLoadingOpenAI = false;

  /**
   * Get Ollama models (from cache or API)
   */
  public getOllamaModels(): Observable<OllamaModel[]> {
    // Check if cache is valid
    if (this.isCacheValid(this.ollamaCache)) {
      return this.ollamaModels$.asObservable();
    }

    // Load from API if not already loading
    if (!this.isLoadingOllama) {
      this.loadOllamaModels();
    }

    return this.ollamaModels$.asObservable();
  }

  /**
   * Get OpenAI models (from cache or API)
   */
  public getOpenAIModels(): Observable<OpenAIModel[]> {
    // Check if cache is valid
    if (this.isCacheValid(this.openaiCache)) {
      return this.openaiModels$.asObservable();
    }

    // Load from API if not already loading
    if (!this.isLoadingOpenAI) {
      this.loadOpenAIModels();
    }

    return this.openaiModels$.asObservable();
  }

  /**
   * Manually invalidate Ollama cache (force reload)
   */
  public invalidateOllamaCache(): void {
    this.ollamaCache = null;
    this.loadOllamaModels();
  }

  /**
   * Manually invalidate OpenAI cache (force reload)
   */
  public invalidateOpenAICache(): void {
    this.openaiCache = null;
    this.loadOpenAIModels();
  }

  /**
   * Clear all caches
   */
  public clearCache(): void {
    this.ollamaCache = null;
    this.openaiCache = null;
    this.ollamaModels$.next([]);
    this.openaiModels$.next([]);
  }

  /**
   * Load Ollama models from API
   */
  private async loadOllamaModels(): Promise<void> {
    this.isLoadingOllama = true;

    try {
      const response = await firstValueFrom(
        this.http.get<{ models: OllamaModel[] }>(this.apiConfig.endpoints.ollama.tags)
      );

      const models = response.models || [];

      // Update cache
      this.ollamaCache = {
        data: models,
        timestamp: Date.now()
      };

      // Emit new data
      this.ollamaModels$.next(models);
    } catch (error) {
      console.error('Error loading Ollama models:', error);
      // Keep old cache on error
    } finally {
      this.isLoadingOllama = false;
    }
  }

  /**
   * Load OpenAI models from API
   */
  private async loadOpenAIModels(): Promise<void> {
    this.isLoadingOpenAI = true;

    try {
      const response = await firstValueFrom(
        this.http.get<{ models: OpenAIModel[] }>(this.apiConfig.endpoints.openai.models)
      );

      const models = response.models || [];

      // Update cache
      this.openaiCache = {
        data: models,
        timestamp: Date.now()
      };

      // Emit new data
      this.openaiModels$.next(models);
    } catch (error) {
      console.error('Error loading OpenAI models:', error);
      // Keep old cache on error
    } finally {
      this.isLoadingOpenAI = false;
    }
  }

  /**
   * Check if cache entry is still valid (within TTL)
   */
  private isCacheValid<T>(cache: CacheEntry<T> | null): boolean {
    if (!cache) {
      return false;
    }

    const age = Date.now() - cache.timestamp;
    return age < this.CACHE_TTL;
  }
}
