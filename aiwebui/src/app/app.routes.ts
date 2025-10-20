import {Routes} from '@angular/router';
import { AuthGuard } from './guards/auth.guard';

export const routes: Routes = [
    {path: '', redirectTo: '/ai-chat', pathMatch: 'full'},
    {
        path: 'login',
        loadComponent: () => import('./auth/login/login.component').then(m => m.LoginComponent)
    },
    {
        path: 'ai-chat',
        canActivate: [AuthGuard],
        loadComponent: () => import('./pages/ai-chat/ai-chat.component').then(m => m.AiChatComponent)
    },
    {
        path: 'openai-chat',
        canActivate: [AuthGuard],
        loadComponent: () => import('./pages/openai-chat/openai-chat.component').then(m => m.OpenaiChatComponent)
    },
    {
        path: 'songgen',
        canActivate: [AuthGuard],
        loadComponent: () => import('./pages/song-generator/song-generator.component').then(m => m.SongGeneratorComponent)
    },
    {
        path: 'songview',
        canActivate: [AuthGuard],
        loadComponent: () => import('./pages/song-view/song-view.component').then(m => m.SongViewComponent)
    },
    {
        path: 'song-sketch-creator',
        canActivate: [AuthGuard],
        loadComponent: () => import('./pages/song-sketch-creator/song-sketch-creator.component').then(m => m.SongSketchCreatorComponent)
    },
    {
        path: 'song-sketch-library',
        canActivate: [AuthGuard],
        loadComponent: () => import('./pages/song-sketch-library/song-sketch-library.component').then(m => m.SongSketchLibraryComponent)
    },
    {
        path: 'lyriccreation',
        canActivate: [AuthGuard],
        loadComponent: () => import('./pages/lyric-creation/lyric-creation.component').then(m => m.LyricCreationComponent)
    },
    {
        path: 'music-style-prompt',
        canActivate: [AuthGuard],
        loadComponent: () => import('./pages/music-style-prompt/music-style-prompt.component').then(m => m.MusicStylePromptComponent)
    },
    {
        path: 'imagegen',
        canActivate: [AuthGuard],
        loadComponent: () => import('./pages/image-generator/image-generator.component').then(m => m.ImageGeneratorComponent)
    },
    {
        path: 'imageview',
        canActivate: [AuthGuard],
        loadComponent: () => import('./pages/image-view/image-view.component').then(m => m.ImageViewComponent)
    },
    {
        path: 'profile',
        canActivate: [AuthGuard],
        loadComponent: () => import('./pages/user-profile/user-profile.component').then(m => m.UserProfileComponent)
    },
    {
        path: 'prompt-templates',
        canActivate: [AuthGuard],
        loadComponent: () => import('./pages/prompt-templates/prompt-templates.component').then(m => m.PromptTemplatesComponent)
    },
    {
        path: 'lyric-parsing-rules',
        canActivate: [AuthGuard],
        loadComponent: () => import('./pages/lyric-parsing-rules/lyric-parsing-rules.component').then(m => m.LyricParsingRulesComponent)
    }
];
