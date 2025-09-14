import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { ScrollArea } from "@radix-ui/react-scroll-area";
import { Bot, MessageCircle, Send, User } from "lucide-react";
import { useState } from "react";

type Message = {
  id: number
  content: string
  sender: "user" | "assistant"
  timestamp: Date
  context?: {
    sources: string[]
    relevantSections: string[]
  }
}

export default function Chat() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 1,
      content:
        "Hello! I'm your AI assistant. I can help you find information from the available documents or answer questions about the platform. What would you like to know?",
      sender: "assistant",
      timestamp: new Date(),
    },
  ])
  const [inputMessage, setInputMessage] = useState("")
  const [isTyping, setIsTyping] = useState(false)

  return (
    <div className="container mx-auto px-4 py-6">
      <div className="max-w-4xl mx-auto">
        <Card className="h-[700px] flex flex-col">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <MessageCircle className="h-5 w-5" />
              AI-jonus
            </CardTitle>
            <CardDescription>Ask questions to AI Aajonus</CardDescription>
          </CardHeader>

          <CardContent className="flex-1 flex flex-col">
            {/* Messages Area */}
            <ScrollArea className="flex-1 pr-4 mb-4">
              <div className="space-y-4">
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex gap-3 ${message.sender === "user" ? "justify-end" : "justify-start"}`}
                  >
                    {message.sender === "assistant" && (
                      <div className="flex-shrink-0">
                        <div className="w-8 h-8 bg-primary rounded-full flex items-center justify-center">
                          <Bot className="h-4 w-4 text-primary-foreground" />
                        </div>
                      </div>
                    )}

                    <div
                      className={`max-w-[80%] rounded-lg px-4 py-2 ${message.sender === "user"
                        ? "bg-primary text-primary-foreground"
                        : "bg-muted text-muted-foreground"
                        }`}
                    >
                      <p className="text-sm leading-relaxed">{message.content}</p>
                      {message.sender === "assistant" && message.context && (
                        <div className="mt-3 pt-3 border-t border-border/50">
                          {message.context.sources.length > 0 && (
                            <div className="mb-2">
                              <p className="text-xs font-medium opacity-80 mb-1">Sources:</p>
                              <div className="flex flex-wrap gap-1">
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
                              <p className="text-xs font-medium opacity-80 mb-1">Referenced sections:</p>
                              <ul className="text-xs opacity-70 space-y-1">
                                {message.context.relevantSections.map((section, index) => (
                                  <li key={index} className="flex items-start gap-1">
                                    <span className="text-primary">•</span>
                                    <span>{section}</span>
                                  </li>
                                ))}
                              </ul>
                            </div>
                          )}
                        </div>
                      )}
                      <p className="text-xs opacity-70 mt-1">
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
              </div>
            </ScrollArea>

            {/* Input Area */}
            <div className="border-t pt-4">
              <div className="flex gap-2">
                <Textarea
                  placeholder="Ask a question about the documents..."
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  // onKeyPress={handleKeyPress}
                  className="flex-1 min-h-[60px] max-h-[120px] resize-none"
                  disabled={isTyping}
                />
                <Button
                  // onClick={handleSendMessage}
                  disabled={!inputMessage.trim() || isTyping}
                  className="self-end"
                >
                  <Send className="h-4 w-4" />
                </Button>
              </div>
              <p className="text-xs text-muted-foreground mt-2">Press Enter to send, Shift+Enter for new line</p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
