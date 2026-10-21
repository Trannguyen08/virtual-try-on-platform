import React, { useEffect, useRef, useState } from 'react';
import { askStylistChat } from '../../api/aiApi';
import '../../styles/aiChatWidget.css';

interface Message {
  id: string;
  sender: 'user' | 'bot';
  text: string;
  isRefusal?: boolean;
  source?: string;
  time: string;
}

const DEFAULT_WELCOME: Message = {
  id: 'welcome-msg',
  sender: 'bot',
  text: 'Xin chào! Em là Stylist AI của V-Fit. Em có thể giúp anh/chị tư vấn size chuẩn xác theo vóc dáng, giải đáp phom dáng trang phục hoặc gợi ý cách phối đồ thời thượng hôm nay ạ! ✨',
  time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
};

const QUICK_CHIPS = [
  '👕 Cao 1m70 nặng 65kg lấy size gì?',
  '✨ Áo này phối với quần gì đẹp nhất?',
  '📏 Form dáng áo này ôm hay rộng rãi?',
];

export const AiStylistChatWidget: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([DEFAULT_WELCOME]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    if (isOpen) {
      scrollToBottom();
    }
  }, [messages, isOpen]);

  const handleSendMessage = async (queryText?: string) => {
    const textToSend = (queryText || inputText).trim();
    if (!textToSend || isLoading) return;

    const userMessage: Message = {
      id: `usr_${Date.now()}`,
      sender: 'user',
      text: textToSend,
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages((prev) => [...prev, userMessage]);
    if (!queryText) setInputText('');
    setIsLoading(true);

    try {
      const response = await askStylistChat({
        query: textToSend,
        height_cm: 170,
        weight_kg: 65,
        garment_category: 'tshirt',
        fit_preference: 'regular',
      });

      const botReply: Message = {
        id: `bot_${Date.now()}`,
        sender: 'bot',
        text: response.reply,
        isRefusal: response.is_refusal,
        source: response.source,
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };

      setMessages((prev) => [...prev, botReply]);
    } catch (err) {
      const errorMessage: Message = {
        id: `bot_err_${Date.now()}`,
        sender: 'bot',
        text: 'Xin lỗi anh/chị, kết nối tới Stylist tạm thời bị gián đoạn. Anh/chị vui lòng thử lại sau giây lát nhé!',
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <>
      {/* 1. Floating Launcher Button */}
      <button
        type="button"
        className="vfit-chat-fab"
        onClick={() => setIsOpen((prev) => !prev)}
        aria-label="Mở Trợ lý Stylist AI"
        title="Trò chuyện với AI Stylist tư vấn may đo & phối đồ"
      >
        <div className="vfit-chat-fab-avatar">
          👗
          <div className="vfit-chat-fab-status" />
        </div>
        <span className="vfit-chat-fab-text">Stylist AI</span>
      </button>

      {/* 2. Expandable Chat Window */}
      {isOpen && (
        <aside className="vfit-chat-window" aria-label="Khung trò chuyện cùng Stylist AI">
          {/* Header */}
          <div className="vfit-chat-header">
            <div className="vfit-chat-header-info">
              <div className="vfit-chat-header-avatar">✨</div>
              <div>
                <h4 className="vfit-chat-header-title">AI Fashion Stylist</h4>
                <p className="vfit-chat-header-sub">
                  <span className="vfit-chat-header-dot" />
                  Trực tuyến 24/7 • Deep Learning M4
                </p>
              </div>
            </div>
            <button
              type="button"
              className="vfit-chat-close-btn"
              onClick={() => setIsOpen(false)}
              aria-label="Đóng khung chat"
            >
              ✕
            </button>
          </div>

          {/* Messages Container */}
          <div className="vfit-chat-messages">
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`vfit-chat-bubble ${msg.sender === 'user' ? 'user' : 'bot'}`}
              >
                {msg.isRefusal && (
                  <div className="vfit-chat-refusal-tag">
                    🛡️ AI Guardrail: Câu hỏi ngoài phạm vi thời trang
                  </div>
                )}
                <div style={{ whiteSpace: 'pre-line' }}>{msg.text}</div>
                <div
                  style={{
                    fontSize: '0.65rem',
                    color: msg.sender === 'user' ? '#cbd5e1' : '#94a3b8',
                    textAlign: msg.sender === 'user' ? 'right' : 'left',
                    marginTop: '0.35rem',
                  }}
                >
                  {msg.time}
                </div>
              </div>
            ))}

            {isLoading && (
              <div className="vfit-chat-bubble bot">
                <div className="vfit-typing-dots">
                  <span />
                  <span />
                  <span />
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Quick chips */}
          <div className="vfit-chat-chips">
            {QUICK_CHIPS.map((chip) => (
              <button
                key={chip}
                type="button"
                className="vfit-chat-chip"
                onClick={() => handleSendMessage(chip)}
              >
                {chip}
              </button>
            ))}
          </div>

          {/* Input Footer */}
          <div className="vfit-chat-footer">
            <input
              type="text"
              className="vfit-chat-input"
              placeholder="Nhập câu hỏi cho Stylist..."
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={isLoading}
            />
            <button
              type="button"
              className="vfit-chat-send-btn"
              onClick={() => handleSendMessage()}
              disabled={isLoading || !inputText.trim()}
              aria-label="Gửi tin nhắn"
            >
              <svg width="15" height="15" fill="none" stroke="currentColor" strokeWidth="2.5" viewBox="0 0 24 24">
                <path d="M5 12h14M12 5l7 7-7 7" />
              </svg>
            </button>
          </div>
        </aside>
      )}
    </>
  );
};
