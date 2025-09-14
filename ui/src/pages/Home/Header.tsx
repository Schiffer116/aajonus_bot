import { Button } from "@/components/ui/button";
import { BookOpen, FileText, MessageCircle, Moon, Search, Sun } from "lucide-react";
import { Link, redirect, useLocation } from "react-router";

type HeaderProps = {
  isDarkMode: boolean;
  toggleDarkMode: () => void;
}

export default function Header(props: HeaderProps) {
  const { pathname: activeTab } = useLocation()
  const { isDarkMode, toggleDarkMode } = props;

  return (
    <header className="sticky top-0 z-50 border-b bg-card/95 backdrop-blur supports-[backdrop-filter]:bg-card/60">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <BookOpen className="h-6 w-6 text-primary" />
            <h1 className="text-xl font-bold text-foreground">Aajonus</h1>
          </div>
          <div className="flex items-center gap-4">
            <Button variant="ghost" size="icon" onClick={toggleDarkMode} className="h-9 w-9">
              {isDarkMode ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
            </Button>
            <Link to="/browse">
              <Button
                variant={activeTab === "/browse" ? "default" : "ghost"}
                className="flex items-center gap-2"
              >
                <Search className="h-4 w-4" />
                Browse
              </Button>
            </Link>
            <Link to="/document">
              <Button
                variant={activeTab.includes("/document") ? "default" : "ghost"}
                onClick={() => redirect("/document")}
                className="flex items-center gap-2"
              >
                <FileText className="h-4 w-4" />
                Document
              </Button>
            </Link>
            <Link to="/chat">
              <Button
                variant={activeTab === "/chat" ? "default" : "ghost"}
                onClick={() => redirect("/chat")}
                className="flex items-center gap-2"
              >
                <MessageCircle className="h-4 w-4" />
                Chat
              </Button>
            </Link>
          </div>
        </div>
      </div>
    </header>
  )
}
