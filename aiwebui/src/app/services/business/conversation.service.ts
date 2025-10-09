import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import {
  Conversation,
  ConversationListResponse,
  ConversationDetailResponse,
  SendMessageResponse,
  ConversationCreateRequest,
  OllamaModel
} from '../../models/conversation.model';
import { environment } from '../../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class ConversationService {
  private readonly baseUrl = `${environment.apiUrl}/api/v1`;

  constructor(private http: HttpClient) {}

  /**
   * List all conversations for the authenticated user
   */
  public getConversations(skip: number = 0, limit: number = 20): Observable<ConversationListResponse> {
    const params = new HttpParams()
      .set('skip', skip.toString())
      .set('limit', limit.toString());

    return this.http.get<ConversationListResponse>(
      `${this.baseUrl}/conversations`,
      { params }
    );
  }

  /**
   * Get a specific conversation with its messages
   */
  public getConversation(id: string): Observable<ConversationDetailResponse> {
    return this.http.get<ConversationDetailResponse>(
      `${this.baseUrl}/conversations/${id}`
    );
  }

  /**
   * Create a new conversation
   */
  public createConversation(data: ConversationCreateRequest): Observable<Conversation> {
    return this.http.post<Conversation>(
      `${this.baseUrl}/conversations`,
      data
    );
  }

  /**
   * Delete a conversation
   */
  public deleteConversation(id: string): Observable<{ message: string }> {
    return this.http.delete<{ message: string }>(
      `${this.baseUrl}/conversations/${id}`
    );
  }

  /**
   * Send a message in a conversation and get AI response
   */
  public sendMessage(conversationId: string, content: string): Observable<SendMessageResponse> {
    return this.http.post<SendMessageResponse>(
      `${this.baseUrl}/conversations/${conversationId}/messages`,
      { content }
    );
  }

  /**
   * Get available Ollama models
   */
  public getModels(): Observable<{ models: OllamaModel[] }> {
    return this.http.get<{ models: OllamaModel[] }>(
      `http://10.0.1.120:11434/api/tags`
    );
  }
}
