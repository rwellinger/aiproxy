import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { ApiConfigService } from './api-config.service';
import { PromptConfigService } from './prompt-config.service';
import { LyricArchitectureService } from '../lyric-architecture.service';
import { firstValueFrom } from 'rxjs';

/**
 * ⚠️ CRITICAL: Single Entry Point for Ollama + Prompt Template Integration
 *
 * This service is the ONLY place where Ollama should be called with database templates.
 *
 * MANDATORY WORKFLOW:
 * 1. Load Prompt Template from DB (via PromptConfigService)
 * 2. Validate required fields (model, temperature, max_tokens MUST be set)
 * 3. Call unified endpoint: /api/v1/ollama/chat/generate-unified
 *
 * ❌ NEVER:
 * - Direct Ollama API calls in other services
 * - Bypass validateAndCallUnified() for template-based operations
 * - Use templates before they exist in DB (backend has no data!)
 * - Implement custom Ollama integration in new features
 *
 * ✅ ALWAYS:
 * - Use validateAndCallUnified(category, action, inputText) for simple cases
 * - Follow its pattern for complex cases (see generateLyricsWithArchitecture, improveLyricSection)
 * - Ensure templates exist in DB first (check prompt_templates table)
 * - Use this.apiConfig.endpoints.ollama.chatGenerateUnified
 *
 * WHY? This is NOT a direct Ollama proxy - it's a Template-Driven Generation System.
 * Templates MUST be in DB first, otherwise backend has no configuration to work with.
 */

interface UnifiedChatRequest {
  pre_condition: string;
  post_condition: string;
  input_text: string;
  user_instructions?: string;
  temperature?: number;
  max_tokens?: number;
  model?: string;
  category?: string;
  action?: string;
}


export interface ChatResponse {
  model: string;
  created_at: string;
  response: string;
  done: boolean;
  done_reason: string;
  total_duration: number;
  load_duration: number;
  prompt_eval_count: number;
  prompt_eval_duration: number;
  eval_count: number;
  eval_duration: number;
}

@Injectable({
  providedIn: 'root'
})
export class ChatService {
  private http = inject(HttpClient);
  private apiConfig = inject(ApiConfigService);
  private promptConfig = inject(PromptConfigService);
  private architectureService = inject(LyricArchitectureService);

  async validateAndCallUnified(category: string, action: string, inputText: string): Promise<string> {
    const template = await firstValueFrom(this.promptConfig.getPromptTemplateAsync(category, action));
    if (!template) {
      throw new Error(`Template ${category}/${action} not found in database`);
    }

    // Validate template has all required parameters
    if (!template.model) {
      throw new Error(`Template ${category}/${action} is missing model parameter`);
    }
    if (template.temperature === undefined || template.temperature === null) {
      throw new Error(`Template ${category}/${action} is missing temperature parameter`);
    }
    if (!template.max_tokens) {
      throw new Error(`Template ${category}/${action} is missing max_tokens parameter`);
    }

    const request: UnifiedChatRequest = {
      pre_condition: template.pre_condition || '',
      post_condition: template.post_condition || '',
      input_text: inputText,
      temperature: template.temperature,
      max_tokens: template.max_tokens,
      model: template.model,
      category: category,
      action: action
    };

    const data: ChatResponse = await firstValueFrom(
      this.http.post<ChatResponse>(this.apiConfig.endpoints.ollama.chatGenerateUnified, request)
    );
    return data.response;
  }

  async improveImagePrompt(prompt: string): Promise<string> {
    return this.validateAndCallUnified('image', 'enhance', prompt);
  }

  async improveImagePromptFast(prompt: string): Promise<string> {
    return this.validateAndCallUnified('image', 'enhance-fast', prompt);
  }

  async enhanceCoverPrompt(prompt: string): Promise<string> {
    return this.validateAndCallUnified('image', 'enhance-cover', prompt);
  }

  async improveMusicStylePrompt(prompt: string): Promise<string> {
    return this.validateAndCallUnified('music', 'enhance', prompt);
  }

  async improveMusicStylePromptForSuno(prompt: string, gender?: 'male' | 'female'): Promise<string> {
    const template = await firstValueFrom(this.promptConfig.getPromptTemplateAsync('music', 'enhance-suno'));
    if (!template) {
      throw new Error('Template music/enhance-suno not found in database');
    }

    // Validate template has all required parameters
    if (!template.model) {
      throw new Error('Template music/enhance-suno is missing model parameter');
    }
    if (template.temperature === undefined || template.temperature === null) {
      throw new Error('Template music/enhance-suno is missing temperature parameter');
    }
    if (!template.max_tokens) {
      throw new Error('Template music/enhance-suno is missing max_tokens parameter');
    }

    // Enhance pre_condition with gender preference if specified
    let enhancedPreCondition = template.pre_condition || '';
    if (gender) {
      const genderInstruction = gender === 'male'
        ? '\n\nVocal preference: Male voice with natural pitch (avoid unnaturally high male vocals)'
        : '\n\nVocal preference: Female voice with natural pitch';
      enhancedPreCondition += genderInstruction;
    }

    const request: UnifiedChatRequest = {
      pre_condition: enhancedPreCondition,
      post_condition: template.post_condition || '',
      input_text: prompt,
      temperature: template.temperature,
      max_tokens: template.max_tokens,
      model: template.model,
      category: 'music',
      action: 'enhance-suno'
    };

    const data: ChatResponse = await firstValueFrom(
      this.http.post<ChatResponse>(this.apiConfig.endpoints.ollama.chatGenerateUnified, request)
    );
    return data.response;
  }

  async generateLyrics(inputText: string): Promise<string> {
    return this.generateLyricsWithArchitecture(inputText);
  }

  async generateLyricsWithArchitecture(inputText: string): Promise<string> {
    const template = await firstValueFrom(this.promptConfig.getPromptTemplateAsync('lyrics', 'generate'));
    if (!template) {
      throw new Error(`Template lyrics/generate not found in database`);
    }

    // Get current architecture configuration
    const architectureString = this.architectureService.generateArchitectureString();
    // Enhance pre_condition with architecture if it exists
    let enhancedPreCondition = template.pre_condition || '';
    if (architectureString.trim()) {
      enhancedPreCondition = architectureString + '\n\n' + enhancedPreCondition;
    }

    // Validate template has all required parameters
    if (!template.model) {
      throw new Error(`Template lyrics/generate is missing model parameter`);
    }
    if (template.temperature === undefined || template.temperature === null) {
      throw new Error(`Template lyrics/generate is missing temperature parameter`);
    }
    if (!template.max_tokens) {
      throw new Error(`Template lyrics/generate is missing max_tokens parameter`);
    }

    const request: UnifiedChatRequest = {
      pre_condition: enhancedPreCondition,
      post_condition: template.post_condition || '',
      input_text: inputText,
      temperature: template.temperature,
      max_tokens: template.max_tokens,
      model: template.model,
      category: 'lyrics',
      action: 'generate'
    };

    const data: ChatResponse = await firstValueFrom(
      this.http.post<ChatResponse>(this.apiConfig.endpoints.ollama.chatGenerateUnified, request)
    );
    return data.response;
  }

  async translateLyric(prompt: string): Promise<string> {
    return this.validateAndCallUnified('lyrics', 'translate', prompt);
  }

  async translateMusicStylePrompt(prompt: string): Promise<string> {
    return this.validateAndCallUnified('music', 'translate', prompt);
  }

  async translateImagePrompt(prompt: string): Promise<string> {
    return this.validateAndCallUnified('image', 'translate', prompt);
  }

  async interpretLyricPrompt(lyric: string): Promise<string> {
    return this.validateAndCallUnified('image', 'interpret-lyric', lyric);
  }

  async generateTitle(inputText: string): Promise<string> {
    return this.validateAndCallUnified('titel', 'generate', inputText);
  }

  async generateTitleFast(inputText: string): Promise<string> {
    return this.validateAndCallUnified('titel', 'generate-fast', inputText);
  }

  async improveLyricSection(
    sectionLabel: string,
    sectionContent: string,
    fullContext: string,
    userInstructions?: string
  ): Promise<string> {
    const template = await firstValueFrom(this.promptConfig.getPromptTemplateAsync('lyrics', 'improve-section'));
    if (!template) {
      throw new Error('Template lyrics/improve-section not found in database');
    }

    // Validate template has all required parameters
    if (!template.model) {
      throw new Error('Template lyrics/improve-section is missing model parameter');
    }
    if (template.temperature === undefined || template.temperature === null) {
      throw new Error('Template lyrics/improve-section is missing temperature parameter');
    }
    if (!template.max_tokens) {
      throw new Error('Template lyrics/improve-section is missing max_tokens parameter');
    }

    // Enhance pre_condition with section label and full context
    let enhancedPreCondition = template.pre_condition || '';
    enhancedPreCondition = `You are improving only the "${sectionLabel}" section.\n\nFull song context:\n${fullContext}\n\n${enhancedPreCondition}`;

    const request: UnifiedChatRequest = {
      pre_condition: enhancedPreCondition,
      post_condition: template.post_condition || '',
      input_text: sectionContent,
      user_instructions: userInstructions || '',
      temperature: template.temperature,
      max_tokens: template.max_tokens,
      model: template.model,
      category: 'lyrics',
      action: 'improve-section'
    };

    const data: ChatResponse = await firstValueFrom(
      this.http.post<ChatResponse>(this.apiConfig.endpoints.ollama.chatGenerateUnified, request)
    );
    return data.response;
  }

  async rewriteLyricSection(sectionContent: string, userInstructions?: string): Promise<string> {
    const template = await firstValueFrom(this.promptConfig.getPromptTemplateAsync('lyrics', 'rewrite-section'));
    if (!template) {
      throw new Error('Template lyrics/rewrite-section not found in database');
    }

    // Validate template has all required parameters
    if (!template.model) {
      throw new Error('Template lyrics/rewrite-section is missing model parameter');
    }
    if (template.temperature === undefined || template.temperature === null) {
      throw new Error('Template lyrics/rewrite-section is missing temperature parameter');
    }
    if (!template.max_tokens) {
      throw new Error('Template lyrics/rewrite-section is missing max_tokens parameter');
    }

    const request: UnifiedChatRequest = {
      pre_condition: template.pre_condition || '',
      post_condition: template.post_condition || '',
      input_text: sectionContent,
      user_instructions: userInstructions || '',
      temperature: template.temperature,
      max_tokens: template.max_tokens,
      model: template.model,
      category: 'lyrics',
      action: 'rewrite-section'
    };

    const data: ChatResponse = await firstValueFrom(
      this.http.post<ChatResponse>(this.apiConfig.endpoints.ollama.chatGenerateUnified, request)
    );
    return data.response;
  }

  async optimizeLyricPhrasing(lyricContent: string, userInstructions?: string): Promise<string> {
    const template = await firstValueFrom(this.promptConfig.getPromptTemplateAsync('lyrics', 'optimize-phrasing'));
    if (!template) {
      throw new Error('Template lyrics/optimize-phrasing not found in database');
    }

    // Validate template has all required parameters
    if (!template.model) {
      throw new Error('Template lyrics/optimize-phrasing is missing model parameter');
    }
    if (template.temperature === undefined || template.temperature === null) {
      throw new Error('Template lyrics/optimize-phrasing is missing temperature parameter');
    }
    if (!template.max_tokens) {
      throw new Error('Template lyrics/optimize-phrasing is missing max_tokens parameter');
    }

    const request: UnifiedChatRequest = {
      pre_condition: template.pre_condition || '',
      post_condition: template.post_condition || '',
      input_text: lyricContent,
      user_instructions: userInstructions || '',
      temperature: template.temperature,
      max_tokens: template.max_tokens,
      model: template.model,
      category: 'lyrics',
      action: 'optimize-phrasing'
    };

    const data: ChatResponse = await firstValueFrom(
      this.http.post<ChatResponse>(this.apiConfig.endpoints.ollama.chatGenerateUnified, request)
    );
    return data.response;
  }

  async extendLyricSection(sectionContent: string, lines: number, userInstructions?: string): Promise<string> {
    const template = await firstValueFrom(this.promptConfig.getPromptTemplateAsync('lyrics', 'extend-section'));
    if (!template) {
      throw new Error('Template lyrics/extend-section not found in database');
    }

    // Validate template has all required parameters
    if (!template.model) {
      throw new Error('Template lyrics/extend-section is missing model parameter');
    }
    if (template.temperature === undefined || template.temperature === null) {
      throw new Error('Template lyrics/extend-section is missing temperature parameter');
    }
    if (!template.max_tokens) {
      throw new Error('Template lyrics/extend-section is missing max_tokens parameter');
    }

    // Enhance pre_condition with line count instruction
    let enhancedPreCondition = template.pre_condition || '';
    enhancedPreCondition = `Add ${lines} more lines to this section.\n\n${enhancedPreCondition}`;

    const request: UnifiedChatRequest = {
      pre_condition: enhancedPreCondition,
      post_condition: template.post_condition || '',
      input_text: sectionContent,
      user_instructions: userInstructions || '',
      temperature: template.temperature,
      max_tokens: template.max_tokens,
      model: template.model,
      category: 'lyrics',
      action: 'extend-section'
    };

    const data: ChatResponse = await firstValueFrom(
      this.http.post<ChatResponse>(this.apiConfig.endpoints.ollama.chatGenerateUnified, request)
    );
    return data.response;
  }
}
