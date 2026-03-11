import { Injectable, signal } from '@angular/core';
import { GoogleGenAI, Chat } from '@google/genai';

export type MessageType = 'text' | 'heuristic' | 'log' | 'audit_denial' | 'audit_granted' | 'error';
export interface Message { id: number; sender: 'user' | 'assistant'; type: MessageType; content: any; }

// Scientific Panel Data Structures
export interface ContextPayload { directives: string; cards: string; logs: string; user: string; tokens: number; }
export interface LibrarianAction { timestamp: string; message: string; type: 'injection' | 'upsert' | 'audit' | 'consolidation'; }
export interface ActiveCard { entity_id: string; priority_weight: number; last_accessed: string; content: object; }
export interface SystemHealth { ollama: 'connected' | 'down'; proxy: string; lastConsolidation: string; tokenBurnRate: number; }


@Injectable({ providedIn: 'root' })
export class ChatService {
  private chat: Chat | null = null;
    
  // Scientific Panel Signals
  private contextPayload = signal<ContextPayload>({ directives: '', cards: '', logs: '', user: '', tokens: 0 });
  private librarianActions = signal<LibrarianAction[]>([]);
  private activeCards = signal<ActiveCard[]>([]);
  private systemHealth = signal<SystemHealth>({ ollama: 'connected', proxy: '8000 bound', lastConsolidation: '3m 14s ago', tokenBurnRate: 0 });

  constructor() {
    try {
      const ai = new GoogleGenAI({ apiKey: (process.env as any).API_KEY });
      this.chat = ai.chats.create({ model: 'gemini-2.5-flash' });
      this.generateInitialScientificData();
    } catch (e) {
      console.error("Could not initialize Gemini AI. Make sure API_KEY is set.", e);
    }
  }

  // Public getters for readonly signals
  getContextPayload = () => this.contextPayload.asReadonly();
  getLibrarianActions = () => this.librarianActions.asReadonly();
  getActiveCards = () => this.activeCards.asReadonly();
  getSystemHealth = () => this.systemHealth.asReadonly();

  getInitialMessages(): Message[] { return []; }

  async *sendMessage(prompt: string, history: Message[]): AsyncGenerator<string> {
    this.updateScientificData(prompt, history);

    if (!this.chat) {
      yield 'Error: Chat service not initialized. Check API Key configuration.';
      return;
    }
    try {
      const result = await this.chat.sendMessageStream({ message: prompt });
      for await (const chunk of result) {
        yield chunk.text;
      }
    } catch (e) {
      console.error("Error sending message to Gemini:", e);
      yield `Error: Could not get a response from the model.`;
    }
  }
  
  private generateInitialScientificData() {
    this.activeCards.set([
      { entity_id: 'PERSON_brenda_01', priority_weight: 8.2, last_accessed: '2m ago', content: { relation: 'former colleague', status: 'hostile' } },
      { entity_id: 'GPU_loop_alpha', priority_weight: 9.8, last_accessed: '1m ago', content: { status: 'open', alert: 'temp > 95C' } }
    ]);
  }
  
  private updateScientificData(prompt: string, history: Message[]) {
    // FIX: Removed explicit `LibrarianAction` type. `mockLibrarianActions` objects
    // lack a timestamp, causing a type mismatch. Type is now correctly inferred.
    const newAction = this.mockLibrarianActions[this.librarianActions().length % this.mockLibrarianActions.length];
    this.librarianActions.update(actions => [{...newAction, timestamp: new Date().toLocaleTimeString()}, ...actions]);

    const directives = 'SYSTEM_PROMPT: You are a helpful assistant.';
    const cards = `INJECTED_CARDS: ${JSON.stringify(this.activeCards().map(c => c.entity_id))}`;
    const logs = `RECALLED_LOGS: log_8f3a2d`;
    const tokens = (directives.length + cards.length + logs.length + prompt.length);

    this.contextPayload.set({
        directives,
        cards,
        logs,
        user: prompt,
        tokens
    });
    
    this.systemHealth.update(h => ({...h, tokenBurnRate: Math.floor(tokens / 10) / 100}));
  }

  private mockLibrarianActions: Omit<LibrarianAction, 'timestamp'>[] = [
      { message: 'Injected 3 cards (Brenda, GPU_loop, Horizon_rel)', type: 'injection' },
      { message: 'Card upsert: PERSON_brenda_01 – appended betrayal event, weight +1.8', type: 'upsert' },
      { message: 'Audit request → denied (fidelity 96.2%)', type: 'audit' },
      { message: 'Consolidation complete – pruned 2 low-weight loops', type: 'consolidation' }
  ];
}
