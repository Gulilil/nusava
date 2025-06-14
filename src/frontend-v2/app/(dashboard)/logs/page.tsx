"use client"
import { Navbar } from "@/components/navbar"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Heart, MessageCircle, UserPlus, Clock, CheckCircle2, XCircle, Settings, RefreshCw } from "lucide-react"
import { useState, useEffect } from "react"
import { ActionLog, PaginationInfo } from "@/types/types"
import { useRouter } from "next/navigation"
import Cookies from "js-cookie"

export default function LogsPage() {
  const router = useRouter()
  const [logs, setLogs] = useState<ActionLog[]>([])
  const [loading, setLoading] = useState(true)
  const [mounted, setMounted] = useState(false)

  const [pagination, setPagination] = useState<PaginationInfo | null>(null)
  const [filters, setFilters] = useState({
    action_type: '',
    status: 'all',
    page: 1
  })

  const handleUnauthorized = () => {
    Cookies.remove("auth")
    localStorage.removeItem("jwtToken")
    localStorage.removeItem("jwtRefresh")
    router.push("/login")
  }
  const API = process.env.NEXT_PUBLIC_API_BASE_URL

  useEffect(() => {
    setMounted(true)
  }, [])

  useEffect(() => {
    if (mounted) {
      loadLogs()
    }
  }, [filters, mounted])

  const loadLogs = async () => {
    setLoading(true)
    try {
      const token = localStorage.getItem('jwtToken')
      if (!token) return

      const params = new URLSearchParams({
        page: filters.page.toString(),
        page_size: '20',
        ...(filters.action_type && { action_type: filters.action_type }),
        ...(filters.status !== 'all' && { status: filters.status })
      })

      const response = await fetch(`${API}/logs/?${params}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      })

      if (response.status === 401) {
        handleUnauthorized()
        return
      }

      if (response.ok) {
        const result = await response.json()
        setLogs(result.data)
        setPagination(result.pagination)
      }
    } catch (error) {
      console.error('Error loading logs:', error)
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

  const handlePageChange = (newPage: number) => {
    setFilters(prev => ({ ...prev, page: newPage }))
  }

  const formatTimestamp = (timestamp: string) => {
    if (!mounted) return '' // Return empty string during SSR
    const date = new Date(timestamp)
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString()
  }
  return (
    <div className="flex flex-col min-h-screen">
      <Navbar title="Action Logs" />
      <main className="flex-1 p-6 space-y-6">
        <Card>
          <CardHeader>
            <CardTitle>Filter Logs</CardTitle>
            <CardDescription>Search and filter through your bot&apos;s action history</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex gap-4">
              <div className="flex-1">
                <Input
                  placeholder="Search action type..."
                  value={filters.action_type}
                  onChange={(e) => setFilters(prev => ({ ...prev, action_type: e.target.value, page: 1 }))}
                  className="max-w-sm"
                />
              </div>
              <Select
                value={filters.status}
                onValueChange={(value) => setFilters(prev => ({ ...prev, status: value, page: 1 }))}
              >
                <SelectTrigger className="max-w-sm">
                  <SelectValue placeholder="Filter by status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Statuses</SelectItem>
                  <SelectItem value="success">Success</SelectItem>
                  <SelectItem value="error">Error</SelectItem>
                  <SelectItem value="failed">Failed</SelectItem>
                </SelectContent>
              </Select>
              <Button onClick={loadLogs} variant="outline" size="icon">
                <RefreshCw className="h-4 w-4" />
              </Button>
            </div>
          </CardContent>
        </Card>

        <Tabs defaultValue="table" className="space-y-4">
          <TabsList>
            <TabsTrigger value="table">Table View</TabsTrigger>
            <TabsTrigger value="detailed">Detailed View</TabsTrigger>
          </TabsList>

          <TabsContent value="table" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Action Logs</CardTitle>
                <CardDescription>
                  {pagination && `Showing ${pagination.total_count} total logs`}
                </CardDescription>
              </CardHeader>
              <CardContent>
                {loading ? (
                  <div className="flex items-center justify-center h-32">
                    <div className="text-lg">Loading logs...</div>
                  </div>
                ) : (
                  <>
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>Type</TableHead>
                          <TableHead>Target</TableHead>
                          <TableHead>Status</TableHead>
                          <TableHead>Message</TableHead>
                          <TableHead>Time</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {logs.map((log) => (
                          <TableRow key={log.id}>
                            <TableCell>
                              <div className="flex items-center gap-2">
                                {getActivityIcon(log.action_type)}
                                <span className="capitalize">{log.action_type}</span>
                              </div>
                            </TableCell>
                            <TableCell className="max-w-xs truncate" title={log.target}>
                              {log.target || '-'}
                            </TableCell>
                            <TableCell>{getStatusBadge(log.status)}</TableCell>
                            <TableCell className="max-w-md truncate" title={log.message}>
                              {log.message}
                            </TableCell>
                            <TableCell className="text-sm text-muted-foreground">
                              {formatTimestamp(log.timestamp)}
                            </TableCell>
                          </TableRow>
                        ))}
                        {logs.length === 0 && (
                          <TableRow>
                            <TableCell colSpan={5} className="text-center text-muted-foreground py-8">
                              No logs found matching your filters
                            </TableCell>
                          </TableRow>
                        )}
                      </TableBody>
                    </Table>

                    {/* Pagination */}
                    {pagination && pagination.total_pages > 1 && (
                      <div className="flex items-center justify-between mt-4">
                        <div className="text-sm text-muted-foreground">
                          Page {pagination.current_page} of {pagination.total_pages}
                        </div>
                        <div className="flex gap-2">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handlePageChange(pagination.current_page - 1)}
                            disabled={!pagination.has_previous}
                          >
                            Previous
                          </Button>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handlePageChange(pagination.current_page + 1)}
                            disabled={!pagination.has_next}
                          >
                            Next
                          </Button>
                        </div>
                      </div>
                    )}
                  </>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="detailed" className="space-y-4">
            <div className="grid gap-4">
              {loading ? (
                <div className="flex items-center justify-center h-32">
                  <div className="text-lg">Loading logs...</div>
                </div>
              ) : (
                logs.map((log) => (
                  <Card key={log.id}>
                    <CardHeader className="pb-3">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          {getActivityIcon(log.action_type)}
                          <CardTitle className="text-lg capitalize">{log.action_type}</CardTitle>
                        </div>
                        {getStatusBadge(log.status)}
                      </div>
                      <CardDescription>{formatTimestamp(log.timestamp)}</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-2">
                        {log.target && (
                          <div>
                            <span className="text-sm font-medium">Target: </span>
                            <span className="text-sm text-muted-foreground">{log.target}</span>
                          </div>
                        )}
                        <div>
                          <span className="text-sm font-medium">Message: </span>
                          <span className="text-sm text-muted-foreground">{log.message}</span>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))
              )}
            </div>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  )
}