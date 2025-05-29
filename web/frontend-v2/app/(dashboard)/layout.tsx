import type React from "react"
import { Sidebar } from "@/components/sidebar"
import { Toaster } from 'sonner';

export default function DashboardLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <div className="flex min-h-screen bg-white dark:bg-gray-950 text-black dark:text-white">
      <Sidebar />
      <Toaster position="top-right"
        closeButton
        richColors
        duration={3000}
      />
      <div className="flex-1 flex flex-col">{children}</div>
    </div>
  )
}
