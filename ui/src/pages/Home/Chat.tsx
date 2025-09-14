// @ts-ignore
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { ScrollArea } from "@/components/ui/scroll-area"
import { Bot, MessageCircle, Send, User } from "lucide-react";
import { useRef, useState } from "react";

type Message = {
  content: string
  sender: "user" | "assistant"
  timestamp: Date
  // context?: {
  //   sources: string[]
  //   relevantSections: string[]
  // }
}

export default function Chat() {
  const idRef = useRef(crypto.randomUUID());
  const [messages, setMessages] = useState<Message[]>([])
  const [inputMessage, setInputMessage] = useState("")
  const [isTyping, setIsTyping] = useState(false)

  async function streamAPI() {
    setIsTyping(true);

    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        id: idRef.current,
        query: inputMessage,
      }),
    });

    if (!res.body) throw new Error("No streaming body available");

    setMessages(prev => [...prev, { content: "", sender: "assistant", timestamp: new Date() }])

    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let response = "";
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value, { stream: true });
      response += chunk;
      setMessages(prev => [
        ...prev.slice(0, prev.length - 1),
        { ...prev[prev.length - 1], content: response }
      ]);

      // setOutput(prev => prev + chunk); // append chunk to state
    }

    setIsTyping(false);
  }


  const handleSendMessage = async () => {
    setMessages(prev => [...prev, { content: inputMessage, sender: "user", timestamp: new Date() }])
    setInputMessage("")
    await streamAPI()
  }

  const handleKeyPress = async (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  return (

    <div className="container mx-auto px-4 py-6">
      <div className="max-w-4xl mx-auto">
        <div className="h-[calc(100vh-140px)] flex flex-col">
          {/* Header */}
          <header className="text-center space-y-4 mb-8 flex-shrink-0">
            <div className="flex items-center justify-center gap-2">
              <MessageCircle className="h-6 w-6 text-primary" />
              <h2 className="text-2xl font-bold text-foreground">AI-jonus</h2>
            </div>
            <p className="text-muted-foreground">Ask questions to AI Aajonus</p>
          </header>

          {/* Messages Area */}
          <div className="flex-1 overflow-hidden">
            <ScrollArea className="h-full">
              <div className="space-y-6 p-4">
                {messages.map((message, idx) => (
                  <div
                    key={idx}
                    className={`flex gap-4 ${message.sender === "user" ? "justify-end" : "justify-start"}`}
                  >
                    {message.sender === "assistant" && (
                      <div className="flex-shrink-0">
                        <div className="w-8 h-8 bg-primary rounded-full flex items-center justify-center">
                          <Bot className="h-4 w-4 text-primary-foreground" />
                        </div>
                      </div>
                    )}

                    <div
                      className={`max-w-[85%] ${message.sender === "user"
                        ? "bg-primary text-primary-foreground rounded-2xl px-4 py-3"
                        : "text-foreground"
                        }`}
                    >
                      {message.sender === "assistant" ? (
                        <div className="prose prose-sm max-w-none dark:prose-invert">
                          <p className="leading-relaxed">{message.content}</p>
                        </div>
                      ) : (
                        <p className="leading-relaxed">{message.content}</p>
                      )}

                      {/*
                      {message.sender === "assistant" && message.context && (
                        <div className="mt-4 pt-4 border-t border-border/30">
                          {message.context.sources.length > 0 && (
                            <div className="mb-3">
                              <p className="text-sm font-medium text-muted-foreground mb-2">Sources:</p>
                              <div className="flex flex-wrap gap-2">
                                {message.context.sources.map((source, index) => (
                                  <Badge key={index} variant="outline" className="text-xs">
                                    {source}
                                  </Badge>
                                ))}
                              </div>
                            </div>
                          )}
                          {message.context.relevantSections.length > 0 && (
                            <div>
                              <p className="text-sm font-medium text-muted-foreground mb-2">Referenced sections:</p>
                              <ul className="text-sm text-muted-foreground space-y-1">
                                {message.context.relevantSections.map((section, index) => (
                                  <li key={index} className="flex items-start gap-2">
                                    <span className="text-primary mt-1">•</span>
                                    <span>{section}</span>
                                  </li>
                                ))}
                              </ul>
                            </div>
                          )}
                        </div>
                      )}
                      */}

                      <p className="text-xs text-muted-foreground/70 mt-2">
                        {message.timestamp.toLocaleTimeString([], {
                          hour: "2-digit",
                          minute: "2-digit",
                        })}
                      </p>
                    </div>

                    {message.sender === "user" && (
                      <div className="flex-shrink-0">
                        <div className="w-8 h-8 bg-accent rounded-full flex items-center justify-center">
                          <User className="h-4 w-4 text-accent-foreground" />
                        </div>
                      </div>
                    )}
                  </div>
                ))}

                {
                  isTyping && (
                    messages[messages.length - 1].sender === "user" ||
                    messages[messages.length - 1].content === ""
                  ) && (
                    <div className="flex gap-4 justify-start">
                      <div className="flex-shrink-0">
                        <div className="w-8 h-8 bg-primary rounded-full flex items-center justify-center">
                          <Bot className="h-4 w-4 text-primary-foreground" />
                        </div>
                      </div>
                      <div className="flex items-center space-x-1 text-muted-foreground">
                        <div className="flex space-x-1">
                          <div className="w-2 h-2 bg-current rounded-full animate-bounce [animation-delay:-0.3s]"></div>
                          <div className="w-2 h-2 bg-current rounded-full animate-bounce [animation-delay:-0.15s]"></div>
                          <div className="w-2 h-2 bg-current rounded-full animate-bounce"></div>
                        </div>
                      </div>
                    </div>
                  )
                }
              </div>
            </ScrollArea>
          </div>

          {/* Input Area */}
          <div className="flex-shrink-0 pt-6">
            <div className="flex gap-3 items-end">
              <div className="flex-1">
                <Textarea
                  placeholder="Ask a question about the documents..."
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onKeyDown={handleKeyPress}
                  className="min-h-[60px] max-h-[120px] resize-none rounded-2xl border-2 focus:border-primary/50 transition-colors"
                  disabled={isTyping}
                />
              </div>
              <Button
                onClick={handleSendMessage}
                disabled={!inputMessage.trim() || isTyping}
                size="lg"
                className="rounded-2xl h-[60px] w-[60px] p-0"
              >
                {isTyping ? (
                  <div className="w-4 h-4 border-2 border-t-transparent border-current rounded-full animate-spin" />
                ) : (
                  <Send className="h-5 w-5" />
                )}
              </Button>
            </div>
            <p className="text-xs text-muted-foreground mt-2 text-center">
              Press Enter to send, Shift+Enter for new line
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

