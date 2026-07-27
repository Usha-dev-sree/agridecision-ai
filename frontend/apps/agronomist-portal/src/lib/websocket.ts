/**
 * Real-time WebSocket Manager for Frontend Applications
 * Connects to Notification & Telemetry WebSocket endpoints, handles reconnects, heartbeats,
 * and dispatches live notifications to Redux store.
 */
import { store } from '@/store';

export class AgriWebSocketClient {
  private socket: WebSocket | null = null;
  private url: string;
  private reconnectInterval: number = 3000;
  private isExplicitClose: boolean = false;
  private listeners: Array<(data: any) => void> = [];

  constructor(endpointPath: string = '/ws/notifications') {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;
    this.url = `${protocol}//${host}${endpointPath}`;
  }

  public connect(): void {
    if (this.socket && (this.socket.readyState === WebSocket.OPEN || this.socket.readyState === WebSocket.CONNECTING)) {
      return;
    }

    const token = store.getState().auth.accessToken;
    const authUrl = token ? `${this.url}?token=${encodeURIComponent(token)}` : this.url;

    try {
      this.socket = new WebSocket(authUrl);

      this.socket.onopen = () => {
        console.log('[WebSocket] Connection established:', this.url);
      };

      this.socket.onmessage = (event: MessageEvent) => {
        try {
          const data = JSON.parse(event.data);
          this.listeners.forEach((listener) => listener(data));
        } catch (e) {
          console.warn('[WebSocket] Non-JSON message received:', event.data);
        }
      };

      this.socket.onerror = (error: Event) => {
        console.error('[WebSocket] Connection error:', error);
      };

      this.socket.onclose = () => {
        console.log('[WebSocket] Connection closed.');
        if (!this.isExplicitClose) {
          setTimeout(() => this.connect(), this.reconnectInterval);
        }
      };
    } catch (e) {
      console.error('[WebSocket] Initialization error:', e);
      setTimeout(() => this.connect(), this.reconnectInterval);
    }
  }

  public subscribe(callback: (data: any) => void): () => void {
    this.listeners.push(callback);
    return () => {
      this.listeners = this.listeners.filter((l) => l !== callback);
    };
  }

  public send(data: any): void {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify(data));
    } else {
      console.warn('[WebSocket] Cannot send message, socket is not open.');
    }
  }

  public disconnect(): void {
    this.isExplicitClose = true;
    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }
  }
}

export const wsClient = new AgriWebSocketClient();
