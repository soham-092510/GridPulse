import { LiveTelemetry } from '../types';

type TelemetryCallback = (data: LiveTelemetry) => void;

class WebSocketClient {
  private ws: WebSocket | null = null;
  private subscribers: Set<TelemetryCallback> = new Set();
  private reconnectInterval = 2000;
  private isConnecting = false;

  public connect() {
    if (this.ws && (this.ws.readyState === WebSocket.OPEN || this.ws.readyState === WebSocket.CONNECTING)) {
      return;
    }

    this.isConnecting = true;
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    // When using Vite dev proxy on port 3000, connect to ws://host:3000/ws/live (proxied to backend 8000)
    const wsUrl = `${protocol}//${window.location.host}/ws/live`;

    try {
      this.ws = new WebSocket(wsUrl);

      this.ws.onopen = () => {
        this.isConnecting = false;
        console.log('[WS] Connected to NeighbourFlex telemetry stream');
      };

      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type === 'LIVE_TELEMETRY') {
            this.subscribers.forEach((cb) => cb(data as LiveTelemetry));
          }
        } catch (e) {
          console.error('[WS] Parse error', e);
        }
      };

      this.ws.onclose = () => {
        this.isConnecting = false;
        this.ws = null;
        setTimeout(() => this.connect(), this.reconnectInterval);
      };

      this.ws.onerror = () => {
        this.ws?.close();
      };
    } catch (err) {
      this.isConnecting = false;
      setTimeout(() => this.connect(), this.reconnectInterval);
    }
  }

  public subscribe(cb: TelemetryCallback) {
    this.subscribers.add(cb);
    return () => {
      this.subscribers.delete(cb);
    };
  }

  public isConnected(): boolean {
    return this.ws !== null && this.ws.readyState === WebSocket.OPEN;
  }
}

export const wsClient = new WebSocketClient();
