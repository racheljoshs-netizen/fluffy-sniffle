
/**
 * COMPONENT MAPPING:
 * File: src/components/status-line/status-line.component.ts
 * Component: ContextPaneComponent
 * Description: Displays the 'Loaded Context Window' (Live Mirror) in Scientific Mode.
 * Replaced the original StatusLineComponent.
 */
import { Component, ChangeDetectionStrategy, input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ContextPayload } from '../../services/chat.service';

@Component({
  selector: 'app-context-pane',
  templateUrl: './status-line.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [CommonModule],
  host: {
    'class': 'block h-full overflow-hidden'
  }
})
export class ContextPaneComponent {
  contextPayload = input.required<ContextPayload>();
}
