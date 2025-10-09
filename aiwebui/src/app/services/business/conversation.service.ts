import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import {
  Conversation,
  ConversationListResponse,
  ConversationDetailResponse,
  SendMessageResponse,
  ConversationCreateRequest,
  OllamaModel
} from '../../models/conversation.model';
import { ApiConfigService } from '../config/api-config.service';

@Injectable({
  providedIn: 'root'
})
export class ConversationService {

  constructor(
    private http: HttpClient,
    private apiConfig: ApiConfigService
  ) {}

  /**
   * List all conversations for the authenticated user
   */
  public getConversations(skip: number = 0, limit: number = 20): Observable<ConversationListResponse> {
    return this.http.get<ConversationListResponse>(
      this.apiConfig.endpoints.conversation.list(skip, limit)
    );
  }

  /**
   * Get a specific conversation with its messages
   */
  public getConversation(id: string): Observable<ConversationDetailResponse> {
    return this.http.get<ConversationDetailResponse>(
      this.apiConfig.endpoints.conversation.detail(id)
    );
  }

  /**
   * Create a new conversation
   */
  public createConversation(data: ConversationCreateRequest): Observable<Conversation> {
    return this.http.post<Conversation>(
      this.apiConfig.endpoints.conversation.create,
      data
    );
  }

  /**
   * Update a conversation (title only)
   */
  public updateConversation(id: string, data: { title: string }): Observable<Conversation> {
    return this.http.patch<Conversation>(
      this.apiConfig.endpoints.conversation.update(id),
      data
    );
  }

  /**
   * Delete a conversation
   */
  public deleteConversation(id: string): Observable<{ message: string }> {
    return this.http.delete<{ message: string }>(
      this.apiConfig.endpoints.conversation.delete(id)
    );
  }

  /**
   * Send a message in a conversation and get AI response
   */
  public sendMessage(conversationId: string, content: string): Observable<SendMessageResponse> {
    return this.http.post<SendMessageResponse>(
      this.apiConfig.endpoints.conversation.sendMessage(conversationId),
      { content }
    );
  }

  /**
   * Get available Ollama models
   */
  public getModels(): Observable<{ models: OllamaModel[] }> {
    return this.http.get<{ models: OllamaModel[] }>(
      this.apiConfig.endpoints.ollama.tags
    );
  }

  // LocalStorage methods for System Context persistence
  private readonly STORAGE_KEY = 'aiChatSystemContext';

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
