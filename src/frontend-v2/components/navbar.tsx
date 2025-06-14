"use client";

// import Link from "next/link"
// import Cookies from "js-cookie"
// import { useRouter } from "next/navigation"
import {
  User,
  // Bell,
  // LogOut
} from "lucide-react"
import { ThemeToggle } from "./theme-toggle"

interface NavbarProps {
  title: string;
}

export function Navbar({ title }: NavbarProps) {
  // const router = useRouter()
  // const handleLogout = () => {
  //   Cookies.remove("auth");
  //   localStorage.removeItem("jwtToken");
  //   localStorage.removeItem("jwtRefresh");
  //   router.push("/login")
  // }
  return (
    <div className="border-b dark:border-gray-800">
      <div className="flex h-16 items-center px-4">
        <h1 className="text-xl font-semibold">{title}</h1>
        <div className="ml-auto flex items-center space-x-4">
          <ThemeToggle />
          <div className="relative group">
            <button className="flex items-center space-x-1 p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-800">
              <div className="w-8 h-8 rounded-full bg-gray-200 dark:bg-gray-700 flex items-center justify-center">
                <User className="h-5 w-5" />
              </div>
            </button>
            {/* <div className="absolute right-0 mt-1 w-48 bg-white dark:bg-gray-900 rounded-md shadow-lg py-1 z-10 hidden group-hover:block">
              <Link href="/profile" className="block px-4 py-2 text-sm hover:bg-gray-100 dark:hover:bg-gray-800">
                Profile
              </Link>
              <Link
                href="/settings"
                className="block px-4 py-2 text-sm hover:bg-gray-100 dark:hover:bg-gray-800"
              >
                Settings
              </Link>
              <div className="border-t border-gray-100 dark:border-gray-800"></div>
              <button
                className="flex items-center w-full px-4 py-2 text-sm hover:bg-gray-100 dark:hover:bg-gray-800"
                onClick={handleLogout}
              >
                <LogOut className="h-4 w-4 mr-2" />
                Logout
              </button>
            </div> */}
          </div>
        </div>
      </div>
    </div>
  );
}
