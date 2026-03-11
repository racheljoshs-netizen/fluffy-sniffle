
/**
 * COMPONENT MAPPING:
 * File: src/components/header/header.component.ts
 * Component: ScientificPanelComponent
 * Description: This component manages the 3-pane Scientific Mode layout.
 * It replaced the original HeaderComponent during the dual-mode refactor.
 */
import { Component, ChangeDetectionStrategy, input, output, signal, inject, PLATFORM_ID, ElementRef, viewChild } from '@angular/core';
import { CommonModule, isPlatformBrowser } from '@angular/common';
import { fromEvent } from 'rxjs';
import { takeUntil } from 'rxjs/operators';

import { Message, ContextPayload, LibrarianAction, SystemHealth, ActiveCard } from '../../services/chat.service';
import { ChatAreaComponent } from '../chat-area/chat-area.component';
import { ContextPaneComponent } from '../status-line/status-line.component';
import { ActionsPaneComponent } from '../settings-modal/settings-modal.component';

@Component({
  selector: 'app-scientific-panel',
  templateUrl: './header.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [CommonModule, ChatAreaComponent, ContextPaneComponent, ActionsPaneComponent],
  host: {
    'class': 'block h-full w-full'
  }
})
export class ScientificPanelComponent {
  // Event outputs
  toggleMode = output<void>();

  // Data inputs
  messages = input.required<Message[]>();
  contextPayload = input.required<ContextPayload>();
  librarianActions = input.required<LibrarianAction[]>();
  systemHealth = input.required<SystemHealth>();
  activeCards = input.required<ActiveCard[]>();

  // Pane resizing logic
  private platformId = inject(PLATFORM_ID);
  private hostEl = inject(ElementRef).nativeElement;

  leftPane = viewChild<ElementRef>('leftPane');
  rightPane = viewChild<ElementRef>('rightPane');
  
  ngAfterViewInit() {
    if (isPlatformBrowser(this.platformId)) {
      this.initResizer('resizer1', this.leftPane());
      this.initResizer('resizer2', this.rightPane(), true);
    }
  }

  private initResizer(resizerId: string, paneEl?: ElementRef, reverse: boolean = false) {
    if (!paneEl) return;
    const resizer = this.hostEl.querySelector(`#${resizerId}`);
    if (!resizer) return;

    const mouseDown$ = fromEvent<MouseEvent>(resizer, 'mousedown');
    const mouseMove$ = fromEvent<MouseEvent>(document, 'mousemove');
    const mouseUp$ = fromEvent<MouseEvent>(document, 'mouseup');

    mouseDown$.subscribe(downEvent => {
      downEvent.preventDefault();
      // Disable text selection during drag
      document.body.style.userSelect = 'none';
      document.body.style.cursor = 'col-resize';

      const startX = downEvent.clientX;
      const startWidth = paneEl.nativeElement.offsetWidth;

      mouseMove$.pipe(takeUntil(mouseUp$)).subscribe(moveEvent => {
        const currentX = moveEvent.clientX;
        const diff = reverse ? startX - currentX : currentX - startX;
        const newWidth = Math.max(100, startWidth + diff); // Minimum width 100px
        paneEl.nativeElement.style.width = `${newWidth}px`;
      });

      mouseUp$.subscribe(() => {
        // Reset styles
        document.body.style.userSelect = '';
        document.body.style.cursor = '';
      });
    });
  }
}
