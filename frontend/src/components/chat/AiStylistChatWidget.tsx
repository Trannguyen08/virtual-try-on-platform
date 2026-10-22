import React, { useEffect, useRef, useState } from 'react';
import { askStylistChat } from '../../api/aiApi';
import '../../styles/aiChatWidget.css';

interface Message {
  id: string;
  sender: 'user' | 'bot';
  text: string;
  time: string;
}

const DEFAULT_WELCOME: Message = {
  id: 'welcome-msg',
  sender: 'bot',
  text: 'Xin chào! Mình có thể tư vấn trang phục hoặc trả lời những câu hỏi khác của bạn.',
  time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
};

const QUICK_CHIPS = [
  'Cao 1m70 nặng 65kg lấy size gì?',
  'Áo này phối với quần gì đẹp nhất?',
  'Form dáng áo này ôm hay rộng rãi?',
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
      const response = await askStylistChat({ query: textToSend });

      const botReply: Message = {
        id: `bot_${Date.now()}`,
        sender: 'bot',
        text: response.reply,
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
        aria-label="Mở trợ lý AI"
        title="Trò chuyện với trợ lý AI"
      >
        <span className="vfit-chat-fab-text">Trợ lý AI</span>
      </button>

      {/* 2. Expandable Chat Window */}
      {isOpen && (
        <aside className="vfit-chat-window" aria-label="Khung trò chuyện với trợ lý AI">
          {/* Header */}
          <div className="vfit-chat-header">
            <div className="vfit-chat-header-info">
              <div className="vfit-chat-header-copy">
                <h4 className="vfit-chat-header-title">Trợ lý AI</h4>
                <p className="vfit-chat-header-sub">
                  Hỏi về trang phục và các chủ đề khác
                </p>
              </div>
            </div>
            <button
              type="button"
              className="vfit-chat-close-btn"
              onClick={() => setIsOpen(false)}
              aria-label="Đóng khung chat"
            >
              Đóng
            </button>
          </div>

          {/* Messages Container */}
          <div className="vfit-chat-messages">
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`vfit-chat-bubble ${msg.sender === 'user' ? 'user' : 'bot'}`}
              >
                <div className="vfit-chat-message-text">{msg.text}</div>
                <div
                  style={{
                    fontSize: '0.75rem',
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
              placeholder="Nhập câu hỏi..."
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
              Gửi
            </button>
          </div>
        </aside>
      )}
    </>
  );
};
