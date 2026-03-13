
import { Component, ChangeDetectionStrategy, signal, inject, PLATFORM_ID, afterNextRender } from '@angular/core';
import { isPlatformBrowser } from '@angular/common';
import { CommonModule } from '@angular/common';

import { ScientificPanelComponent } from './components/header/header.component';
import { ChatAreaComponent } from './components/chat-area/chat-area.component';
import { InputBarComponent } from './components/input-bar/input-bar.component';
import { ChatService, Message, ContextPayload, LibrarianAction, SystemHealth, ActiveCard } from './services/chat.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css'],
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [
    CommonModule,
    ScientificPanelComponent,
    ChatAreaComponent,
    InputBarComponent
  ],
  host: {
    '(window:keydown.control.shift.M)': 'toggleMode()'
  }
})
export class AppComponent {
  private chatService = inject(ChatService);
  private platformId = inject(PLATFORM_ID);

  // UI Mode state
  mode = signal<'user' | 'scientific'>('user');

  // Core chat state
  messages = signal<Message[]>([]);
  isLoading = signal(false);
  
  // Scientific Panel state
  contextPayload = this.chatService.getContextPayload();
  librarianActions = this.chatService.getLibrarianActions();
  systemHealth = this.chatService.getSystemHealth();
  activeCards = this.chatService.getActiveCards();

  constructor() {
    afterNextRender(() => {
        if (isPlatformBrowser(this.platformId)) {
            const storedMode = localStorage.getItem('g-pattern-mode') as 'user' | 'scientific';
            if (storedMode) {
                this.mode.set(storedMode);
            }
        }
    });
  }

  toggleMode() {
    this.mode.update(current => {
      const nextMode = current === 'user' ? 'scientific' : 'user';
      if (isPlatformBrowser(this.platformId)) {
        localStorage.setItem('g-pattern-mode', nextMode);
      }
      return nextMode;
    });
  }

  async handleSendMessage(prompt: string) {
    if (!prompt.trim() || this.isLoading()) return;

    this.isLoading.set(true);
    
    // Optimistic UI update
    const userMessage: Message = { id: Date.now(), sender: 'user', type: 'text', content: prompt };
    this.messages.update(msgs => [...msgs, userMessage]);

    const assistantMessageId = Date.now() + 1;
    const assistantMessage: Message = { id: assistantMessageId, sender: 'assistant', type: 'text', content: '▋' };
    this.messages.update(msgs => [...msgs, assistantMessage]);

    try {
      const stream = this.chatService.sendMessage(prompt, this.messages());
      let fullResponse = '';

      for await (const chunk of stream) {
        fullResponse += chunk;
        this.messages.update(msgs => {
          const lastMsg = msgs[msgs.length - 1];
          // Ensure we are updating the correct message
          if (lastMsg && lastMsg.id === assistantMessageId) {
            lastMsg.content = fullResponse + '▋';
          }
          return [...msgs]; // Trigger change detection with new array reference
        });
      }

      // Finalize response
      this.messages.update(msgs => {
        const lastMsg = msgs[msgs.length - 1];
        if (lastMsg && lastMsg.id === assistantMessageId) {
          lastMsg.content = fullResponse;
        }
        return [...msgs];
      });
    } catch (e) {
      const errorContent = e instanceof Error ? e.message : 'An unknown error occurred.';
      this.messages.update(msgs => {
         const lastMsg = msgs[msgs.length - 1];
         if (lastMsg && lastMsg.id === assistantMessageId) {
            lastMsg.content = `Critical Error: ${errorContent}`;
            lastMsg.type = 'error';
         }
         return [...msgs];
      });
    } finally {
      this.isLoading.set(false);
    }
  }
}
