/* eslint-disable @typescript-eslint/no-explicit-any */
"use client"

import React, { useState } from "react"
import { useRouter } from "next/navigation"
import { Instagram } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Alert, AlertDescription } from "@/components/ui/alert"
import Cookies from "js-cookie";
import axios from "axios";

const API = process.env.NEXT_PUBLIC_API_BASE_URL;

export default function LoginPage() {
  const router = useRouter()
  const [username, setUsername] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState("")
  const [success, setSuccess] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [isRegisterMode, setIsRegisterMode] = useState(false)

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setSuccess("");
    setIsLoading(true);

    try {
      const res = await axios.post(`${API}/login/`, { username, password });
      if (res.data && res.data.access) {
        Cookies.set("auth", res.data.access, { expires: 7 });
        localStorage.setItem("jwtToken", res.data.access);
        localStorage.setItem("jwtRefresh", res.data.refresh);
        router.push("/");
      } else {
        setError(res.data.message || "Login failed");
      }
    } catch (err: any) {
      setError(err.response?.data?.message || "Login failed");
    } finally {
      setIsLoading(false);
    }
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setSuccess("");
    setIsLoading(true);

    try {
      const res = await axios.post(`${API}/register/`, { username, password });
      if (res.data) {
        setSuccess("Registration successful! You can now login.");
        setIsRegisterMode(false);
        setUsername("");
        setPassword("");
        Cookies.set("auth", res.data.access, { expires: 7 });
        localStorage.setItem("jwtToken", res.data.access);
        localStorage.setItem("jwtRefresh", res.data.refresh);
        router.push("/");
      } else {
        setError(res.data.message || "Registration failed");
      }
    } catch (err: any) {
      setError(err.response?.data?.message || "Registration failed");
    } finally {
      setIsLoading(false);
    }
  };

  const toggleMode = () => {
    setIsRegisterMode(!isRegisterMode);
    setError("");
    setSuccess("");
    setUsername("");
    setPassword("");
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-100 dark:bg-gray-900 p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="space-y-1">
          <div className="flex justify-center mb-4">
            <div className="rounded-full bg-pink-600 p-2">
              <Instagram className="h-8 w-8 text-white" />
            </div>
          </div>
          <CardTitle className="text-2xl text-center">Nusava Bot Dashboard</CardTitle>
          <CardDescription className="text-center">
            {isRegisterMode
              ? "Create your account to access the dashboard"
              : "Enter your Instagram credential to access your dashboard"
            }
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={isRegisterMode ? handleRegister : handleLogin}>
            {error && (
              <Alert variant="destructive" className="mb-4">
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}
            {success && (
              <Alert className="mb-4 border-green-500 bg-green-50 text-green-700">
                <AlertDescription>{success}</AlertDescription>
              </Alert>
            )}
            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="username">Username</Label>
                <Input
                  id="username"
                  placeholder="Enter your username"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="password">Password</Label>
                <Input
                  id="password"
                  type="password"
                  placeholder="Enter your password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                />
              </div>
            </div>
          </form>
        </CardContent>
        <CardFooter className="flex flex-col space-y-3">
          <Button
            className="w-full"
            onClick={isRegisterMode ? handleRegister : handleLogin}
            disabled={isLoading}
          >
            {isLoading
              ? (isRegisterMode ? "Registering..." : "Logging in...")
              : (isRegisterMode ? "Register" : "Login")
            }
          </Button>
          <Button
            variant="outline"
            className="w-full"
            onClick={toggleMode}
            disabled={isLoading}
          >
            {isRegisterMode ? "Already have an account? Login" : "Don't have an account? Register"}
          </Button>
        </CardFooter>
      </Card>
    </div>
  )
}