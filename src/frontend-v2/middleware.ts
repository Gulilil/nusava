import { NextResponse } from "next/server"
import type { NextRequest } from "next/server"

export function middleware(request: NextRequest) {
  const token = request.cookies.get("auth")?.value;
  const isLoggedIn = Boolean(token); // is there a JWT token?
  const isLoginPage = request.nextUrl.pathname === "/login";

  // Not logged in, trying to access anything except /login → redirect to /login
  if (!isLoggedIn && !isLoginPage) {
    return NextResponse.redirect(new URL("/login", request.url));
  }

  // Already logged in, trying to access /login → redirect to /
  if (isLoggedIn && isLoginPage) {
    return NextResponse.redirect(new URL("/", request.url));
  }

  // Otherwise, allow
  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!api|_next/static|_next/image|favicon.ico).*)"],
}
