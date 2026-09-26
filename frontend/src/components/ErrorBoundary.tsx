import React, { Component, ErrorInfo, ReactNode } from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';

interface Props {
  children: ReactNode;
  compact?: boolean;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('[NeighbourFlex Error Boundary Caught]:', error, errorInfo);
  }

  private handleReset = () => {
    this.setState({ hasError: false, error: null });
  };

  private handleReload = () => {
    this.setState({ hasError: false, error: null });
    window.location.reload();
  };

  public render() {
    if (this.state.hasError) {
      if (this.props.compact) {
        return (
          <div className="py-12 flex items-center justify-center p-4">
            <div className="max-w-md w-full glass-card rounded-2xl p-6 shadow-lg border border-amber-200 text-center">
              <div className="mx-auto w-10 h-10 rounded-full bg-amber-100 flex items-center justify-center text-amber-600 mb-3">
                <AlertTriangle className="h-5 w-5" />
              </div>
              <h3 className="text-sm font-bold text-slate-900">View Temporarily Interrupted</h3>
              <p className="mt-1.5 text-xs text-slate-600 leading-relaxed">
                A transient telemetry or rendering error occurred. Live data stream is still active.
              </p>
              <div className="mt-3 p-2 bg-slate-50 border border-slate-200 rounded text-[10px] font-mono text-slate-600 text-left overflow-auto max-h-20">
                {this.state.error?.message || 'Transient state error'}
              </div>
              <div className="mt-4 flex items-center justify-center space-x-2">
                <button
                  onClick={this.handleReset}
                  className="inline-flex items-center space-x-1.5 rounded-xl bg-emerald-600 px-3.5 py-1.5 text-xs font-bold text-white hover:bg-emerald-500 transition shadow-xs"
                >
                  <RefreshCw className="h-3.5 w-3.5" />
                  <span>Retry View</span>
                </button>
                <button
                  onClick={this.handleReload}
                  className="inline-flex items-center space-x-1.5 rounded-xl border border-slate-200 bg-white px-3 py-1.5 text-xs font-semibold text-slate-700 hover:bg-slate-50 transition shadow-xs"
                >
                  <span>Reload App</span>
                </button>
              </div>
            </div>
          </div>
        );
      }

      return (
        <div className="min-h-screen bg-slate-50 flex items-center justify-center p-6">
          <div className="max-w-md w-full glass-card rounded-2xl p-6 shadow-lg border border-red-200 text-center">
            <div className="mx-auto w-12 h-12 rounded-full bg-red-100 flex items-center justify-center text-red-600 mb-3">
              <AlertTriangle className="h-6 w-6" />
            </div>
            <h2 className="text-base font-bold text-slate-900">Dashboard Interrupted</h2>
            <p className="mt-2 text-xs text-slate-600 leading-relaxed">
              A temporary telemetry rendering glitch was intercepted. Click below to restore live telemetry.
            </p>
            <div className="mt-3 p-2 bg-slate-100 rounded text-[10px] font-mono text-slate-700 text-left overflow-auto max-h-24">
              {this.state.error?.message || 'Unknown render error'}
            </div>
            <button
              onClick={this.handleReload}
              className="mt-4 inline-flex items-center space-x-2 rounded-xl bg-emerald-600 px-4 py-2 text-xs font-bold text-white hover:bg-emerald-500 transition shadow-sm"
            >
              <RefreshCw className="h-3.5 w-3.5" />
              <span>Resume Live Dashboard</span>
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
