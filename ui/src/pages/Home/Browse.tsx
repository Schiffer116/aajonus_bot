import { FileText, Search, X } from "lucide-react"
import { useState } from "react"
import { Link, useLoaderData, useSearchParams, type LoaderFunctionArgs } from "react-router"
import { type QueryClient } from "@tanstack/react-query"

import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"

import { categories, type Document } from "./Home"


export const browseLoader = (queryClient: QueryClient) => async ({ request }: LoaderFunctionArgs) => {
  const currentUrl = new URL(request.url);
  const query = currentUrl.searchParams.get("query");

  const docs: Document[] = await queryClient.ensureQueryData({
    queryKey: ["query", query],
    queryFn: async () => {
      const apiUrl = new URL("/api/documents", currentUrl.origin);
      if (query) apiUrl.searchParams.set("query", query);

      return fetch(apiUrl).then((res) => res.json());
    }
  })

  return docs
}

export default function Browse() {
  const [searchParams, setSearchParams] = useSearchParams()
  const documents = useLoaderData() as Awaited<ReturnType<ReturnType<typeof browseLoader>>>

  const [searchQuery, setSearchQuery] = useState(searchParams.get("query") || "")
  const [searchCategory, setSearchCategory] = useState(searchParams.get("category") || "All")

  const handleSearch = async () => {
    if (searchQuery.trim() !== "") {
      setSearchParams((searchParams) => {
        searchParams.set("query", searchQuery);
        return searchParams;
      })
    } else {
      setSearchParams((searchParams) => {
        searchParams.delete("query");
        return searchParams;
      })
    }
  }

  const handleCategoryChange = (category: string) => {
    if (category == "All") {
      setSearchParams((searchParams) => {
        searchParams.delete("category");
        return searchParams;
      })
    } else {
      setSearchParams((searchParams) => {
        searchParams.set("category", category);
        return searchParams;
      })
    }
    setSearchCategory(category);
  }

  const filteredDocuments = documents.filter(doc =>
    searchCategory === "All" || doc.category.includes(searchCategory)
  )

  return (
    <div className="container mx-auto px-4 py-6">
      <div className="max-w-3xl mx-auto">
        <div className="space-y-8">
          <header className="text-center space-y-4">
            <h2 className="text-2xl font-bold text-foreground">Browse Documents</h2>
            <p className="text-muted-foreground">Search and select documents to read</p>
          </header>

          {/* Search Section */}
          <div className="space-y-4 mx-20">
            <div className="flex gap-4 items-center">
              <div className="relative flex-1">
                <Input
                  placeholder="Semantic search..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyDown={(e) => { if (e.key === "Enter") handleSearch() }}
                />
                {searchQuery && (
                  <Button
                    variant="ghost"
                    onClick={() => setSearchQuery("")}
                    className="absolute right-2 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground hover:text-foreground transition-colors"
                  >
                    <X />
                  </Button>
                )}
              </div>
              <Button onClick={handleSearch} className="flex items-center gap-2">
                <Search className="h-4 w-4" />
              </Button>
            </div>

            <div className="flex flex-wrap justify-center gap-2">
              {categories.map((cat, idx) => (
                <Button
                  key={idx}
                  variant={searchCategory === cat ? "default" : "outline"}
                  className="text-xs"
                  onClick={() => handleCategoryChange(cat)}
                >
                  {cat}
                </Button>
              ))}
            </div>
          </div>

          <div className="space-y-4">
            <div className="text-muted-foreground text-sm">
              {searchParams.get("query") && filteredDocuments.length + " results"}
            </div>

            {filteredDocuments.map((doc, idx) => (
              <Link
                to={`/document/${doc.id}${doc.chunk ? "?highlight=" + encodeURIComponent(doc.chunk) : ""}`}
                key={idx}
                className="block p-6 rounded-lg border cursor-pointer transition-all duration-200 hover:shadow-md hover:border-primary/30"
              >
                <div className="space-y-3">
                  <div className="flex items-start justify-between gap-4">
                    <h3 className="font-semibold text-lg text-foreground leading-tight flex-1">{doc.name}</h3>
                    <Badge variant="outline" className="text-xs shrink-0">
                      {doc.category}
                    </Badge>
                  </div>

                  {doc.chunk && (
                    <div className="bg-muted/50 p-4 rounded-md border-l-3 border-primary/40">
                      <p className="text-sm text-muted-foreground leading-relaxed">{doc.chunk}</p>
                    </div>
                  )}
                </div>
              </Link>
            ))}

            {filteredDocuments.length === 0 && (
              <div className="text-center py-12">
                <FileText className="h-12 w-12 mx-auto mb-4 opacity-30" />
                <p className="text-muted-foreground">No documents found matching your search.</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
