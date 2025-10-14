import {Injectable} from '@angular/core';
import {environment} from '../../../environments/environment';

@Injectable({
    providedIn: 'root'
})
export class ApiConfigService {
    private readonly baseUrl = environment.apiUrl;

    // API Endpoints
    readonly endpoints = {
        song: {
            generate: `${this.baseUrl}/api/v1/song/generate`,
            status: (taskId: string) => `${this.baseUrl}/api/v1/song/task/status/${taskId}`,
            tasks: `${this.baseUrl}/api/v1/song/tasks`,
            stems: `${this.baseUrl}/api/v1/song/stem/generate`,
            list: (limit?: number, offset?: number, status?: string) => {
                const params = new URLSearchParams();
                if (limit !== undefined) params.append('limit', limit.toString());
                if (offset !== undefined) params.append('offset', offset.toString());
                if (status) params.append('status', status);
                const query = params.toString();
                return `${this.baseUrl}/api/v1/song/list${query ? '?' + query : ''}`;
            },
            detail: (songId: string) => `${this.baseUrl}/api/v1/song/id/${songId}`,
            delete: (songId: string) => `${this.baseUrl}/api/v1/song/id/${songId}`,
            update: (songId: string) => `${this.baseUrl}/api/v1/song/id/${songId}`,
            updateChoiceRating: (choiceId: string) => `${this.baseUrl}/api/v1/song/choice/${choiceId}/rating`,
            bulkDelete: `${this.baseUrl}/api/v1/song/bulk-delete`
        },
        image: {
            generate: `${this.baseUrl}/api/v1/image/generate`,
            status: (taskId: string) => `${this.baseUrl}/api/v1/image/status/${taskId}`,
            tasks: `${this.baseUrl}/api/v1/image/tasks`,
            list: (limit?: number, offset?: number) => `${this.baseUrl}/api/v1/image/list${limit !== undefined || offset !== undefined ? '?' : ''}${limit !== undefined ? `limit=${limit}` : ''}${limit !== undefined && offset !== undefined ? '&' : ''}${offset !== undefined ? `offset=${offset}` : ''}`,
            detail: (id: string) => `${this.baseUrl}/api/v1/image/id/${id}`,
            delete: (id: string) => `${this.baseUrl}/api/v1/image/id/${id}`,
            update: (id: string) => `${this.baseUrl}/api/v1/image/id/${id}`,
            bulkDelete: `${this.baseUrl}/api/v1/image/bulk-delete`
        },
        redis: {
            keys: `${this.baseUrl}/api/v1/redis/list/keys`,
            deleteTask: (taskId: string) => `${this.baseUrl}/api/v1/redis/${taskId}`
        },
        billing: {
            info: `${this.baseUrl}/api/v1/song/mureka-account`
        },
        instrumental: {
            generate: `${this.baseUrl}/api/v1/instrumental/generate`,
            status: (taskId: string) => `${this.baseUrl}/api/v1/instrumental/task/status/${taskId}`
        },
        prompt: {
            list: `${this.baseUrl}/api/v1/prompts`,
            category: (category: string) => `${this.baseUrl}/api/v1/prompts/${category}`,
            specific: (category: string, action: string) => `${this.baseUrl}/api/v1/prompts/${category}/${action}`,
            update: (category: string, action: string) => `${this.baseUrl}/api/v1/prompts/${category}/${action}`,
            create: `${this.baseUrl}/api/v1/prompts`,
            delete: (category: string, action: string) => `${this.baseUrl}/api/v1/prompts/${category}/${action}`
        },
        conversation: {
            list: (skip?: number, limit?: number, provider?: string, archived?: boolean) => {
                const params = new URLSearchParams();
                if (skip !== undefined) params.append('skip', skip.toString());
                if (limit !== undefined) params.append('limit', limit.toString());
                if (provider) params.append('provider', provider);
                if (archived === true) params.append('archived', 'true');
                if (archived === false) params.append('archived', 'false');
                // archived === undefined means default (only non-archived)
                const query = params.toString();
                return `${this.baseUrl}/api/v1/conversations${query ? '?' + query : ''}`;
            },
            detail: (id: string) => `${this.baseUrl}/api/v1/conversations/${id}`,
            create: `${this.baseUrl}/api/v1/conversations`,
            update: (id: string) => `${this.baseUrl}/api/v1/conversations/${id}`,
            delete: (id: string) => `${this.baseUrl}/api/v1/conversations/${id}`,
            sendMessage: (id: string) => `${this.baseUrl}/api/v1/conversations/${id}/messages`,
            compress: (id: string, keepRecent?: number) => {
                const query = keepRecent !== undefined ? `?keep_recent=${keepRecent}` : '';
                return `${this.baseUrl}/api/v1/conversations/${id}/compress${query}`;
            },
            restoreArchive: (id: string) => `${this.baseUrl}/api/v1/conversations/${id}/restore-archive`,
            exportFull: (id: string) => `${this.baseUrl}/api/v1/conversations/${id}/export-full`
        },
        ollama: {
            tags: `${this.baseUrl}/api/v1/ollama/tags`,
            chatModels: `${this.baseUrl}/api/v1/ollama/chat/models`,
            chatGenerateUnified: `${this.baseUrl}/api/v1/ollama/chat/generate-unified`
        },
        openai: {
            models: `${this.baseUrl}/api/v1/openai/chat/models`
        }
    };

    getBaseUrl(): string {
        return this.baseUrl;
    }

    getEndpoint(category: keyof typeof this.endpoints, action: string, ...params: unknown[]): string {
        const categoryEndpoints = this.endpoints[category] as Record<string, unknown>;
        const endpoint = categoryEndpoints[action];
        return typeof endpoint === 'function' ? endpoint(...params) : endpoint as string;
    }
}
