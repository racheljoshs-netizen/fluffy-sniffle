
import { Component, ChangeDetectionStrategy, output, signal, input } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-input-bar',
  templateUrl: './input-bar.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [CommonModule]
})
export class InputBarComponent {
  sendMessage = output<string>();
  openSettings = output<void>();
  isLoading = input(false);

  prompt = signal('');
  
  // Mock token counts
  currentTokens = signal(0);
  maxTokens = 128000;

  onInput(event: Event) {
    const textarea = event.target as HTMLTextAreaElement;
    this.prompt.set(textarea.value);
    // Simple token estimation
    this.currentTokens.set(textarea.value.length);
    this.autoResize(textarea);
  }

  handleKeydown(event: KeyboardEvent) {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      this.submitMessage();
    }
  }

  submitMessage() {
    if (this.prompt().trim() && !this.isLoading()) {
      this.sendMessage.emit(this.prompt());
      this.prompt.set('');
      this.currentTokens.set(0);
    }
  }

  triggerOpenSettings() {
    this.openSettings.emit();
  }
  
  private autoResize(textarea: HTMLTextAreaElement) {
    textarea.style.height = 'auto';
    textarea.style.height = `${textarea.scrollHeight}px`;
  }
}
