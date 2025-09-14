import { useEffect, useState } from "react"

import Header from "./Header"
import { Outlet } from "react-router"

export type Document = {
    id: string
    name: string
    category: string
    chunk?: string
}

export const categories = ["All", "Books", "Interviews", "Misc", "Newsletters", "QNA", "Videos"]
export const tabs = ["browse", "document", "chat"]

export default function Home() {
    const [isDarkMode, setIsDarkMode] = useState(true)

    useEffect(() => {
        if (isDarkMode) {
            document.documentElement.classList.add("dark")
        } else {
            document.documentElement.classList.remove("dark")
        }
    }, [isDarkMode])

    const toggleDarkMode = () => {
        setIsDarkMode(!isDarkMode)
    }

    return (
        <div className={`bg-background ${isDarkMode ? "dark" : ""}`}>

            <Header
                isDarkMode={isDarkMode}
                toggleDarkMode={toggleDarkMode}
            />

            <Outlet />
        </div>
    )
}
