/**
 * Sliding window message buffer for conversation-aware fact extraction.
 * Buffers messages per conversation and flushes when window is full or on timeout.
 */

export interface BufferedMessage {
  sender: string;
  content: string;
  timestamp: number;
}

export interface ConversationBuffer {
  messages: BufferedMessage[];
  lastFlush: number;
}

export interface BufferConfig {
  windowSize: number;       // messages to accumulate (default 8 = 4 Q&A pairs)
  stepSize: number;         // slide by this many (default 4 = 50% overlap)
  flushTimeoutMs: number;   // flush after inactivity (default 5 min)
}

export class MessageBuffer {
  private buffers = new Map<string, ConversationBuffer>();
  private config: BufferConfig;
  private flushCallback: (conversationId: string, block: string) => Promise<void>;
  private flushTimer: ReturnType<typeof setInterval> | null = null;

  constructor(
    config: Partial<BufferConfig>,
    flushCallback: (conversationId: string, block: string) => Promise<void>
  ) {
    this.config = {
      windowSize: config.windowSize || 8,
      stepSize: config.stepSize || 4,
      flushTimeoutMs: config.flushTimeoutMs || 5 * 60 * 1000,
    };
    this.flushCallback = flushCallback;

    // Periodic flush check (every 60s)
    this.flushTimer = setInterval(() => this.flushStale(), 60_000);
  }

  /**
   * Add a message to the buffer for a conversation.
   * Returns true if the buffer was flushed.
   */
  async addMessage(
    conversationId: string,
    sender: string,
    content: string
  ): Promise<boolean> {
    if (!content || content.trim().length < 10) return false;

    let buf = this.buffers.get(conversationId);
    if (!buf) {
      buf = { messages: [], lastFlush: Date.now() };
      this.buffers.set(conversationId, buf);
    }

    buf.messages.push({
      sender,
      content: content.trim(),
      timestamp: Date.now(),
    });

    // Flush when window is full
    if (buf.messages.length >= this.config.windowSize) {
      await this.flush(conversationId);
      return true;
    }

    return false;
  }

  /**
   * Flush a conversation buffer — extract facts from accumulated messages.
   */
  private async flush(conversationId: string): Promise<void> {
    const buf = this.buffers.get(conversationId);
    if (!buf || buf.messages.length === 0) return;

    // Build conversation block
    const block = buf.messages
      .map((m) => `[${m.sender}]: ${m.content}`)
      .join("\n");

    // Slide window: keep last stepSize messages for overlap
    buf.messages = buf.messages.slice(this.config.stepSize);
    buf.lastFlush = Date.now();

    // Process asynchronously
    try {
      await this.flushCallback(conversationId, block);
    } catch (err: any) {
      console.error(
        `[knowledge-graph] Flush error for ${conversationId}: ${err.message}`
      );
    }
  }

  /**
   * Flush all stale buffers (idle for longer than flushTimeoutMs).
   */
  private async flushStale(): Promise<void> {
    const now = Date.now();
    for (const [conversationId, buf] of this.buffers) {
      if (
        buf.messages.length > 0 &&
        now - buf.lastFlush > this.config.flushTimeoutMs
      ) {
        await this.flush(conversationId);
      }
    }
  }

  /**
   * Force flush all buffers (e.g., on shutdown).
   */
  async flushAll(): Promise<void> {
    for (const conversationId of this.buffers.keys()) {
      await this.flush(conversationId);
    }
  }

  /**
   * Stop the periodic flush timer.
   */
  destroy(): void {
    if (this.flushTimer) {
      clearInterval(this.flushTimer);
      this.flushTimer = null;
    }
  }

  /**
   * Get buffer stats.
   */
  getStats(): Record<string, { messageCount: number; lastFlush: number }> {
    const stats: Record<string, { messageCount: number; lastFlush: number }> = {};
    for (const [id, buf] of this.buffers) {
      stats[id] = {
        messageCount: buf.messages.length,
        lastFlush: buf.lastFlush,
      };
    }
    return stats;
  }
}
