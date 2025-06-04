"use client"

import Link from "next/link"
import { usePathname, useRouter } from "next/navigation"
import { useState } from "react"
import {
  BarChart3,
  Settings,
  ClipboardList,
  MousePointerClick,
  Instagram,
  LogOut,
  ChevronLeft,
  ChevronRight,
  ImageIcon,
  User
} from "lucide-react"
import Cookies from "@/node_modules/@types/js-cookie"

import { cn } from "@/lib/utils"

// Navigation routes
const routes = [
  {
    title: "Dashboard",
    icon: BarChart3,
    href: "/dashboard",
    color: "text-sky-500",
  },
  {
    title: "Configuration",
    icon: Settings,
    href: "/config",
    color: "text-violet-500",
  },
  {
    title: "Activity Logs",
    icon: ClipboardList,
    href: "/logs",
    color: "text-pink-700",
  },
  {
    title: "Manual Actions",
    icon: MousePointerClick,
    href: "/actions",
    color: "text-orange-500",
  },
  {
    title: "Posts",
    icon: ImageIcon,
    href: "/posts",
    color: "text-green-500",
  },
  {
    title: "Persona",
    href: "/persona",
    icon: User,
    color: "text-yellow-500",
  },
]

export function Sidebar() {
  const pathname = usePathname()
  const router = useRouter()
  const [collapsed, setCollapsed] = useState(false)

  const handleLogout = () => {
    Cookies.remove("auth");
    localStorage.removeItem("jwtToken");
    localStorage.removeItem("jwtRefresh");
    localStorage.removeItem("igUsername");
    router.push("/login")
  }

  return (
    <div
      className={cn(
        "sticky top-0 h-screen py-4 flex flex-col bg-slate-900 text-white transition-all duration-300",
        collapsed ? "w-20" : "w-64",
      )}
    >
      {/* Toggle button */}
      <button
        onClick={() => setCollapsed(!collapsed)}
        className="absolute -right-3 top-12 bg-slate-900 text-white p-1 rounded-full border border-slate-700 z-10"
      >
        {collapsed ? <ChevronRight size={16} /> : <ChevronLeft size={16} />}
      </button>

      <div className="px-3 py-2 flex-1">
        {/* Logo */}
        <Link href="/" className={cn("flex items-center pl-3 mb-10", collapsed ? "justify-center" : "")}>
          <div className="relative w-8 h-8 mr-4">
            <Instagram className="h-8 w-8 text-pink-600" />
          </div>
          {!collapsed && <h1 className="text-xl font-bold">Nusava</h1>}
        </Link>

        {/* Navigation */}
        <div className="space-y-1">
          {routes.map((route) => (
            <Link
              key={route.href}
              href={route.href}
              className={cn(
                "text-sm group flex p-3 w-full justify-start font-medium cursor-pointer hover:text-white hover:bg-white/10 rounded-lg transition",
                pathname === route.href ? "text-white bg-white/10" : "text-zinc-400",
                collapsed ? "justify-center" : "",
              )}
            >
              <route.icon className={cn("h-5 w-5", route.color, collapsed ? "" : "mr-3")} />
              {!collapsed && route.title}
            </Link>
          ))}
        </div>
      </div>

      {/* Logout button */}
      <div className="px-3 py-2">
        <button
          onClick={handleLogout}
          className={cn(
            "w-full text-zinc-400 hover:text-white hover:bg-white/10 p-3 rounded-lg flex items-center",
            collapsed ? "justify-center" : "",
          )}
        >
          <LogOut className="h-5 w-5 text-red-500" />
          {!collapsed && <span className="ml-3">Logout</span>}
        </button>
      </div>
    </div>
  )
}
