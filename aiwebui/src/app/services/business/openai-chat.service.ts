import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { OpenAIModel } from '../../models/conversation.model';
import { ApiConfigService } from '../config/api-config.service';

@Injectable({
  providedIn: 'root'
})
export class OpenaiChatService {
  private http = inject(HttpClient);
  private apiConfig = inject(ApiConfigService);

  /**
   * Get available OpenAI models
   */
  public getModels(): Observable<{ models: OpenAIModel[] }> {
    return this.http.get<{ models: OpenAIModel[] }>(
      this.apiConfig.endpoints.openai.models
    );
  }

  // LocalStorage methods for System Context persistence
  private readonly STORAGE_KEY = 'openaiChatSystemContext';

  /**
   * Load saved system context from localStorage
   */
  public loadSystemContext(): string {
    return localStorage.getItem(this.STORAGE_KEY) || '';
  }

  /**
   * Save system context to localStorage
   */
  public saveSystemContext(context: string): void {
    if (context.trim()) {
      localStorage.setItem(this.STORAGE_KEY, context);
    } else {
      this.clearSystemContext();
    }
  }

  /**
   * Clear saved system context from localStorage
   */
  public clearSystemContext(): void {
    localStorage.removeItem(this.STORAGE_KEY);
  }
}
