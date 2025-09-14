import { Button } from "@/components/ui/button";
import { FileText } from "lucide-react";
import { useEffect } from "react";
import { useLoaderData, useSearchParams, type LoaderFunctionArgs } from "react-router";

export async function documentLoader({ params }: LoaderFunctionArgs) {
  const { id } = params
  if (!id) return {
    name: "",
    content: "",
  }

  const response = await fetch(`/api/documents/${id}`)
  const data = await response.json()
  return data
}

export default function DocumentViewer() {
  let { name, content } = useLoaderData<typeof documentLoader>()
  const [searchParams] = useSearchParams()


  const highlight = searchParams.get("highlight")
  if (highlight) {
    content = content.replace(
      highlight.trim(),
      `<span id="target" class="bg-yellow-700">${highlight}</span>`
    );
  }

  const scrollToHighlight = () => {
    document.getElementById("target")?.scrollIntoView({ behavior: "smooth", block: "center" })
  }

  useEffect(() => {
    if (!name) return

    document.title = name;
    scrollToHighlight()

    return () => {
      document.title = "Aajonus Vonderplanitz"
    }
  }, [])

  return (
    <div className="container mx-auto px-4 py-6 max-w-4xl">
      <article className="min-h-[calc(100vh-140px)] bg-background">
        {content !== "" ? (
          <div>
            <header className="mb-8 pb-6 border-b border-border/20">
              <div className="text-center space-y-3">
                <h1 className="text-3xl font-bold text-balance text-foreground leading-tight">
                  {name}
                </h1>
              </div>
            </header>

            <div className="prose max-w-none dark:prose-invert whitespace-break-spaces prose-blockquote:mb-4"
              dangerouslySetInnerHTML={{ __html: content }}
            />

          </div>
        ) : (
          <div className="flex items-center justify-center h-full">
            <div className="text-center text-muted-foreground">
              <FileText className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p className="text-lg font-medium mb-2">No Document Selected</p>
              <p className="text-sm">Go to Browse to select a document to read</p>
            </div>
          </div>
        )}
      </article>

      {
        highlight && (
          <Button
            variant="outline"
            className="sticky bottom-4 left-4 flex items-center gap-2"
            onClick={() => scrollToHighlight()}
          >
            Highlight
          </Button>
        )
      }
    </div>
  )
}
