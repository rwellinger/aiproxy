import { Component, OnInit, OnDestroy, ViewChild, ElementRef, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Subject, takeUntil } from 'rxjs';
import { MatSnackBarModule } from '@angular/material/snack-bar';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatSelectModule } from '@angular/material/select';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatExpansionModule } from '@angular/material/expansion';
import { MatProgressBarModule } from '@angular/material/progress-bar';

import { ConversationService } from '../../services/business/conversation.service';
import { NotificationService } from '../../services/ui/notification.service';
import {
  Conversation,
  Message,
  OllamaModel,
  ConversationDetailResponse
} from '../../models/conversation.model';
import { MessageContentPipe } from '../../pipes/message-content.pipe';

@Component({
  selector: 'app-ai-chat',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatSnackBarModule,
    MatCardModule,
    MatButtonModule,
    MatSelectModule,
    MatFormFieldModule,
    MatInputModule,
    MatIconModule,
    MatProgressSpinnerModule,
    MatExpansionModule,
    MatProgressBarModule,
    MessageContentPipe
  ],
  templateUrl: './ai-chat.component.html',
  styleUrl: './ai-chat.component.scss'
})
export class AiChatComponent implements OnInit, OnDestroy {
  // Services
  private conversationService = inject(ConversationService);
  private notificationService = inject(NotificationService);
  private destroy$ = new Subject<void>();

  // Data
  conversations: Conversation[] = [];
  currentConversation: Conversation | null = null;
  messages: Message[] = [];
  models: OllamaModel[] = [];

  // UI State
  isLoading = false;
  isSending = false;
  isLoadingModels = false;

  // Form State
  newChatTitle = '';
  selectedModel = '';
  systemContext = '';
  messageInput = '';

  // View State
  showNewChatForm = false;

  @ViewChild('messagesContainer') private messagesContainer!: ElementRef;
  @ViewChild('messageInputField') private messageInputField!: ElementRef;

  ngOnInit(): void {
    this.loadModels();
    this.loadConversations();

    // Load saved system context from localStorage
    this.systemContext = this.conversationService.loadSystemContext();
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  /**
   * Load available Ollama models
   */
  private loadModels(): void {
    this.isLoadingModels = true;
    this.conversationService
      .getModels()
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (response) => {
          this.models = response.models || [];
          // Set default model if available
          if (this.models.length > 0 && !this.selectedModel) {
            this.selectedModel = this.models[0].name;
          }
        },
        error: (error) => {
          console.error('Error loading models:', error);
          this.notificationService.error('Failed to load models');
        },
        complete: () => {
          this.isLoadingModels = false;
        }
      });
  }

  /**
   * Load list of conversations
   */
  public loadConversations(): void {
    this.isLoading = true;
    this.conversationService
      .getConversations(0, 50)
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (response) => {
          this.conversations = response.conversations;

          // Auto-select first conversation if none selected
          if (!this.currentConversation && this.conversations.length > 0) {
            this.selectConversation(this.conversations[0]);
          }
        },
        error: (error) => {
          console.error('Error loading conversations:', error);
          this.notificationService.error('Failed to load conversations');
        },
        complete: () => {
          this.isLoading = false;
        }
      });
  }

  /**
   * Select a conversation and load its messages
   */
  public selectConversation(conversation: Conversation): void {
    this.isLoading = true;
    this.currentConversation = conversation;

    this.conversationService
      .getConversation(conversation.id)
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (response: ConversationDetailResponse) => {
          this.messages = response.messages;
          this.currentConversation = response.conversation;
          this.systemContext = response.conversation.system_context || '';
          setTimeout(() => this.scrollToBottom(), 100);
        },
        error: (error) => {
          console.error('Error loading conversation:', error);
          this.notificationService.error('Failed to load conversation');
        },
        complete: () => {
          this.isLoading = false;
        }
      });
  }

  /**
   * Show new chat form
   */
  public showNewChat(): void {
    this.showNewChatForm = true;
    this.newChatTitle = '';
    // Load persisted system context
    this.systemContext = this.conversationService.loadSystemContext();
  }

  /**
   * Cancel new chat creation
   */
  public cancelNewChat(): void {
    this.showNewChatForm = false;
    this.newChatTitle = '';
    // Keep system context - it persists across sessions
  }

  /**
   * Create new conversation
   */
  public createConversation(): void {
    if (!this.newChatTitle.trim() || !this.selectedModel) {
      this.notificationService.error('Please provide a title and select a model');
      return;
    }

    this.isLoading = true;
    this.conversationService
      .createConversation({
        title: this.newChatTitle.trim(),
        model: this.selectedModel,
        system_context: this.systemContext.trim() || undefined
      })
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (conversation) => {
          this.conversations.unshift(conversation);
          this.selectConversation(conversation);
          this.showNewChatForm = false;
          this.newChatTitle = '';
        },
        error: (error) => {
          console.error('Error creating conversation:', error);
          this.notificationService.error('Failed to create conversation');
        },
        complete: () => {
          this.isLoading = false;
        }
      });
  }

  /**
   * Delete current conversation
   */
  public deleteConversation(): void {
    if (!this.currentConversation) return;

    if (!confirm(`Delete conversation "${this.currentConversation.title}"?`)) {
      return;
    }

    const conversationId = this.currentConversation.id;

    this.isLoading = true;
    this.conversationService
      .deleteConversation(conversationId)
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: () => {
          this.conversations = this.conversations.filter(c => c.id !== conversationId);
          this.currentConversation = null;
          this.messages = [];

          // Select first available conversation
          if (this.conversations.length > 0) {
            this.selectConversation(this.conversations[0]);
          }
        },
        error: (error) => {
          console.error('Error deleting conversation:', error);
          this.notificationService.error('Failed to delete conversation');
        },
        complete: () => {
          this.isLoading = false;
        }
      });
  }

  /**
   * Send message in current conversation
   */
  public sendMessage(): void {
    if (!this.currentConversation || !this.messageInput.trim() || this.isSending) {
      return;
    }

    const content = this.messageInput.trim();
    this.messageInput = '';
    this.isSending = true;

    this.conversationService
      .sendMessage(this.currentConversation.id, content)
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (response) => {
          // Add both user and assistant messages to the view
          this.messages.push(response.user_message);
          this.messages.push(response.assistant_message);

          setTimeout(() => this.scrollToBottom(), 100);
          setTimeout(() => this.focusInput(), 200);
        },
        error: (error) => {
          console.error('Error sending message:', error);
          this.notificationService.error('Failed to send message');
          // Restore message input on error
          this.messageInput = content;
        },
        complete: () => {
          this.isSending = false;
        }
      });
  }

  /**
   * Handle Enter key in message input
   */
  public onMessageInputKeydown(event: KeyboardEvent): void {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      this.sendMessage();
    }
  }

  /**
   * Scroll messages to bottom
   */
  private scrollToBottom(): void {
    if (this.messagesContainer) {
      const container = this.messagesContainer.nativeElement;
      container.scrollTop = container.scrollHeight;
    }
  }

  /**
   * Focus message input field
   */
  private focusInput(): void {
    if (this.messageInputField) {
      this.messageInputField.nativeElement.focus();
    }
  }

  /**
   * Format date for display
   */
  public formatDate(dateString: string): string {
    const date = new Date(dateString);
    const today = new Date();
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);

    // Check if today
    if (date.toDateString() === today.toDateString()) {
      return date.toLocaleTimeString('de-CH', {
        hour: '2-digit',
        minute: '2-digit'
      });
    }

    // Check if yesterday
    if (date.toDateString() === yesterday.toDateString()) {
      return `Yesterday ${date.toLocaleTimeString('de-CH', {
        hour: '2-digit',
        minute: '2-digit'
      })}`;
    }

    // Otherwise show full date
    return date.toLocaleDateString('de-CH', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  }

  /**
   * Get message role class for styling
   */
  public getMessageClass(message: Message): string {
    return `message--${message.role}`;
  }

  /**
   * Handle system context changes and save to localStorage
   */
  public onSystemContextChange(): void {
    this.conversationService.saveSystemContext(this.systemContext);
  }

  /**
   * Clear saved system context
   */
  public clearSystemContext(): void {
    this.systemContext = '';
    this.conversationService.clearSystemContext();
  }

  /**
   * Get token usage percentage
   */
  public getTokenPercentage(): number {
    if (!this.currentConversation?.context_window_size || !this.currentConversation?.current_token_count) return 0;
    return (this.currentConversation.current_token_count / this.currentConversation.context_window_size) * 100;
  }

  /**
   * Get formatted token count (e.g., "1.2k / 8k")
   */
  public getFormattedTokenCount(): string {
    if (!this.currentConversation?.context_window_size) return '';

    const format = (num: number): string => {
      if (num >= 1000) return `${(num / 1000).toFixed(1)}k`;
      return num.toString();
    };

    const current = this.currentConversation.current_token_count || 0;
    const max = this.currentConversation.context_window_size;

    return `${format(current)} / ${format(max)}`;
  }

  /**
   * Get progress bar color based on usage
   */
  public getTokenProgressColor(): string {
    const percentage = this.getTokenPercentage();
    if (percentage >= 90) return 'warn';
    if (percentage >= 70) return 'accent';
    return 'primary';
  }

  /**
   * Check if token warning should be shown
   */
  public shouldShowTokenWarning(): boolean {
    return this.getTokenPercentage() >= 90;
  }
}
