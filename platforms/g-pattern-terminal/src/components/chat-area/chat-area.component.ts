
import { Component, ChangeDetectionStrategy, input, signal, ViewChildren, QueryList, ElementRef, afterNextRender } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Message } from '../../services/chat.service';

@Component({
  selector: 'app-chat-area',
  templateUrl: './chat-area.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [CommonModule],
  host: {
    'class': 'block h-full w-full overflow-hidden'
  }
})
export class ChatAreaComponent {
  messages = input.required<Message[]>();
  mode = input<'user' | 'scientific'>('user');
  expandedHeuristics = signal<{[key: number]: boolean}>({});

  @ViewChildren('message') messageElements!: QueryList<ElementRef>;
  
  constructor() {
    afterNextRender(() => {
        this.scrollToBottom();
        this.messageElements.changes.subscribe(() => {
            this.scrollToBottom();
        });
    });
  }

  toggleHeuristic(id: number) {
    this.expandedHeuristics.update(current => ({
      ...current,
      [id]: !current[id]
    }));
  }

  private scrollToBottom(): void {
    try {
        const lastElement = this.messageElements.last?.nativeElement;
        if(lastElement) {
            lastElement.scrollIntoView({ behavior: 'smooth', block: 'end' });
        }
    } catch (err) { 
        console.error('Could not scroll to bottom:', err);
    }
  }

  // Helper to pretty-print JSON content
  prettyPrintJson(content: any): string {
    return JSON.stringify(content, null, 2);
  }
}
