"use client"
import { Navbar } from "@/components/navbar"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"
import { ArrowUpRight, Heart, MessageCircle, UserPlus, Clock, CheckCircle2, XCircle, ArrowRight, Settings } from "lucide-react"
import { useEffect, useState } from "react"
import { Button } from "@/components/ui/button"
import Link from "next/link"
import { ActionLog, ConfigData } from "@/types/types"
import { useRouter } from "next/navigation"
import Cookies from "js-cookie"

const API = process.env.NEXT_PUBLIC_API_BASE_URL

export default function Dashboard() {
  const router = useRouter()
  const [recentActivities, setRecentActivities] = useState<ActionLog[]>([])
  const [botConfig, setBotConfig] = useState<ConfigData | null>(null)
  const [loading, setLoading] = useState(true)
  const handleUnauthorized = () => {
    Cookies.remove("auth")
    localStorage.removeItem("jwtToken")
    localStorage.removeItem("jwtRefresh")
    router.push("/login")
  }
  useEffect(() => {
    loadDashboardData()
  }, [])

  const loadDashboardData = async () => {
    try {
      const token = localStorage.getItem('jwtToken')
      if (!token) return

      // Load recent logs (first 5)
      const logsResponse = await fetch(`${API}/logs/?page_size=5`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      })

      if (logsResponse.status === 401) {
        handleUnauthorized()
        return
      }

      if (logsResponse.ok) {
        const logsResult = await logsResponse.json()
        setRecentActivities(logsResult.data)
      }

      // Load configuration
      const configResponse = await fetch(`${API}/config/`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      })

      if (configResponse.status === 401) {
        handleUnauthorized()
        return
      }
      
      if (configResponse.ok) {
        const configResult = await configResponse.json()
        setBotConfig(configResult.data)
      }
    } catch (error) {
      console.error('Error loading dashboard data:', error)
    } finally {
      setLoading(false)
    }
  }

  const getActivityIcon = (actionType: string) => {
    switch (actionType.toLowerCase()) {
      case 'like':
        return <Heart className="h-4 w-4 text-pink-500" />
      case 'follow':
        return <UserPlus className="h-4 w-4 text-violet-500" />
      case 'comment':
        return <MessageCircle className="h-4 w-4 text-blue-500" />
      default:
        return <Settings className="h-4 w-4 text-gray-500" />
    }
  }

  const getStatusBadge = (status: string) => {
    switch (status.toLowerCase()) {
      case 'success':
        return (
          <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200">
            <CheckCircle2 className="h-3 w-3 mr-1" /> Success
          </Badge>
        )
      case 'error':
      case 'failed':
        return (
          <Badge variant="outline" className="bg-red-50 text-red-700 border-red-200">
            <XCircle className="h-3 w-3 mr-1" /> Failed
          </Badge>
        )
      default:
        return (
          <Badge variant="outline" className="bg-yellow-50 text-yellow-700 border-yellow-200">
            <Clock className="h-3 w-3 mr-1" /> Pending
          </Badge>
        )
    }
  }

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffMins = Math.floor(diffMs / 60000)
    
    if (diffMins < 1) return 'Just now'
    if (diffMins < 60) return `${diffMins} min ago`
    if (diffMins < 1440) return `${Math.floor(diffMins / 60)} hours ago`
    return date.toLocaleDateString()
  }

  return (
    <div className="flex flex-col min-h-screen">
      <Navbar title="Dashboard" />
      <main className="flex-1 p-6 space-y-6">
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Likes</CardTitle>
              <Heart className="h-4 w-4 text-pink-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">1,234</div>
              <p className="text-xs text-muted-foreground">+20.1% from last week</p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Follows</CardTitle>
              <UserPlus className="h-4 w-4 text-violet-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">567</div>
              <p className="text-xs text-muted-foreground">+10.5% from last week</p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Comments</CardTitle>
              <MessageCircle className="h-4 w-4 text-blue-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">321</div>
              <p className="text-xs text-muted-foreground">+5.2% from last week</p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Success Rate</CardTitle>
              <ArrowUpRight className="h-4 w-4 text-green-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">98.2%</div>
              <p className="text-xs text-muted-foreground">+2.1% from last week</p>
            </CardContent>
          </Card>
        </div>

        <Tabs defaultValue="activities" className="space-y-4">
          <TabsList>
            <TabsTrigger value="activities">Recent Activities</TabsTrigger>
            <TabsTrigger value="config">Current Configuration</TabsTrigger>
          </TabsList>
          <TabsContent value="activities" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Recent Bot Activities</CardTitle>
                <CardDescription>The latest actions performed by your Instagram bot</CardDescription>
              </CardHeader>
              <CardContent>
                 {loading ? (
                  <div className="flex items-center justify-center h-32">
                    <div className="text-lg">Loading activities...</div>
                  </div>
                ) : (
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Type</TableHead>
                        <TableHead>Target</TableHead>
                        <TableHead>Status</TableHead>
                        <TableHead>Time</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {recentActivities.map((activity) => (
                        <TableRow key={activity.id}>
                          <TableCell>
                            <div className="flex items-center gap-2">
                              {getActivityIcon(activity.action_type)}
                              <span className="capitalize">{activity.action_type}</span>
                            </div>
                          </TableCell>
                          <TableCell>{activity.target || '-'}</TableCell>
                          <TableCell>{getStatusBadge(activity.status)}</TableCell>
                          <TableCell>{formatTimestamp(activity.timestamp)}</TableCell>
                        </TableRow>
                      ))}
                      {recentActivities.length === 0 && (
                        <TableRow>
                          <TableCell colSpan={4} className="text-center text-muted-foreground py-4">
                            No recent activities
                          </TableCell>
                        </TableRow>
                      )}
                    </TableBody>
                  </Table>
                )}
              </CardContent>
            </Card>
          </TabsContent>
          <TabsContent value="config" className="space-y-4">
            <Card>
              <CardHeader>
              <CardTitle className="flex items-center">
                <Settings className="mr-2 h-5 w-5" />
                Current Bot Configuration
              </CardTitle>
              <CardDescription>Quick overview of your AI assistant settings</CardDescription>
            </CardHeader>
            <CardContent>
              {loading ? (
                  <div className="flex items-center justify-center h-32">
                    <div className="text-lg">Loading configuration...</div>
                  </div>
                ) : botConfig ? (
                  <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                    <div>
                      <h3 className="font-medium">Temperature</h3>
                      <p className="text-sm text-muted-foreground">
                        {botConfig.temperature} (Creativity level)
                      </p>
                    </div>
                    <div>
                      <h3 className="font-medium">Top K</h3>
                      <p className="text-sm text-muted-foreground">
                        {botConfig.top_k} (Vector search limit)
                      </p>
                    </div>
                    <div>
                      <h3 className="font-medium">Max Tokens</h3>
                      <p className="text-sm text-muted-foreground">
                        {botConfig.max_token} (Response length limit)
                      </p>
                      </div>
                      <div>
                      <h3 className="font-medium">Max Iterations</h3>
                      <p className="text-sm text-muted-foreground">
                        {botConfig.max_iteration} (Iteration limit)
                      </p>
                    </div>
                  </div>
                ) : (
                  <div className="text-center text-muted-foreground py-4">
                    Configuration not loaded
                  </div>
                )}
            </CardContent>
            <CardFooter>
              <Button asChild variant="outline" className="w-full sm:w-auto">
                <Link href="/config">
                  Edit Configuration <ArrowRight className="ml-2 h-4 w-4" />
                </Link>
              </Button>
            </CardFooter>
            </Card>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  )
}
