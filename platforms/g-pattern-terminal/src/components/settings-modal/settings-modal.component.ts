
/**
 * COMPONENT MAPPING:
 * File: src/components/settings-modal/settings-modal.component.ts
 * Component: ActionsPaneComponent
 * Description: Displays the 'Librarian & System Actions' pane in Scientific Mode.
 * Replaced the original SettingsModalComponent.
 */
import { Component, ChangeDetectionStrategy, input, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { LibrarianAction, SystemHealth, ActiveCard } from '../../services/chat.service';

@Component({
  selector: 'app-actions-pane',
  templateUrl: './settings-modal.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [CommonModule],
  host: {
    'class': 'block h-full'
  }
})
export class ActionsPaneComponent {
  librarianActions = input.required<LibrarianAction[]>();
  systemHealth = input.required<SystemHealth>();
  activeCards = input.required<ActiveCard[]>();

  expandedSections = signal<{[key: string]: boolean}>({
    health: true,
    cards: true,
    actions: true,
    db: true
  });

  toggleSection(section: string) {
    this.expandedSections.update(current => ({
      ...current,
      [section]: !current[section]
    }));
  }

  copyToClipboard(text: string | object) {
    const str = typeof text === 'string' ? text : JSON.stringify(text, null, 2);
    navigator.clipboard.writeText(str).then(() => {
      // Optional: Add visual feedback here if desired
      console.log('Copied to clipboard');
    });
  }
}
