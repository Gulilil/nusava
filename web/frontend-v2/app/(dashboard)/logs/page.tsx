"use client"

import { useState } from "react"
import { Navbar } from "@/components/navbar"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"
import {
  Heart,
  UserPlus,
  MessageCircle,
  CheckCircle2,
  XCircle,
  Clock,
  Download,
  Share2,
  ImageIcon,
  Mail,
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Input } from "@/components/ui/input"

// Sample data
const allActivities = [
  {
    id: 1,
    type: "like",
    target: "@fashionista",
    targetContent: "Summer collection post",
    status: "success",
    time: "Today, 10:30 AM",
  },
  {
    id: 2,
    type: "follow",
    target: "@travel_lover",
    targetContent: "Profile",
    status: "success",
    time: "Today, 10:25 AM",
  },
  {
    id: 3,
    type: "comment",
    target: "@foodie_blog",
    targetContent: "New recipe post",
    status: "failed",
    time: "Today, 10:20 AM",
  },
  {
    id: 4,
    type: "post",
    target: "https://instagram.com/p/abc123",
    targetContent: "New product launch",
    status: "success",
    time: "Today, 10:15 AM",
  },
  {
    id: 5,
    type: "share",
    target: "@fitness_guru",
    targetContent: "Workout video",
    status: "pending",
    time: "Today, 10:10 AM",
  },
  {
    id: 6,
    type: "dm",
    target: "@art_gallery",
    targetContent: "Exhibition inquiry",
    status: "success",
    time: "Today, 10:05 AM",
  },
  {
    id: 7,
    type: "like",
    target: "@music_lover",
    targetContent: "Concert video",
    status: "success",
    time: "Today, 10:00 AM",
  },
  {
    id: 8,
    type: "share",
    target: "@book_worm",
    targetContent: "Book review post",
    status: "failed",
    time: "Today, 09:55 AM",
  },
  {
    id: 9,
    type: "post",
    target: "https://instagram.com/p/def456",
    targetContent: "Behind the scenes photo",
    status: "success",
    time: "Today, 09:50 AM",
  },
  {
    id: 10,
    type: "dm",
    target: "@pet_lover",
    targetContent: "Collaboration message",
    status: "pending",
    time: "Today, 09:45 AM",
  },
]

export default function LogsPage() {
  const [typeFilter, setTypeFilter] = useState("all")
  const [statusFilter, setStatusFilter] = useState("all")
  const [searchQuery, setSearchQuery] = useState("")

  // Filter activities based on selected filters and search query
  const filteredActivities = allActivities.filter((activity) => {
    // Type filter
    if (typeFilter !== "all" && activity.type !== typeFilter) return false

    // Status filter
    if (statusFilter !== "all" && activity.status !== statusFilter) return false

    // Search query
    if (searchQuery) {
      const query = searchQuery.toLowerCase()
      return (
        activity.target.toLowerCase().includes(query) ||
        activity.targetContent.toLowerCase().includes(query) ||
        activity.type.toLowerCase().includes(query)
      )
    }

    return true
  })

  return (
    <div className="flex flex-col min-h-screen">
      <Navbar title="Activity Logs" />
      <main className="flex-1 p-6 space-y-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle>Bot Activity Logs</CardTitle>
              <CardDescription>Complete history of your Instagram bot activities</CardDescription>
            </div>
            <Button variant="outline" size="sm">
              <Download className="mr-2 h-4 w-4" />
              Export
            </Button>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-4 mb-4">
              <div className="flex-1">
                <Input
                  placeholder="Search logs..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
              </div>
              <Select value={typeFilter} onValueChange={setTypeFilter}>
                <SelectTrigger className="w-[180px]">
                  <SelectValue placeholder="Filter by type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Activities</SelectItem>
                  <SelectItem value="like">Likes</SelectItem>
                  <SelectItem value="follow">Follows</SelectItem>
                  <SelectItem value="comment">Comments</SelectItem>
                  <SelectItem value="post">Posts</SelectItem>
                  <SelectItem value="share">Shares</SelectItem>
                  <SelectItem value="dm">Direct Messages</SelectItem>
                </SelectContent>
              </Select>
              <Select value={statusFilter} onValueChange={setStatusFilter}>
                <SelectTrigger className="w-[180px]">
                  <SelectValue placeholder="Filter by status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Statuses</SelectItem>
                  <SelectItem value="success">Success</SelectItem>
                  <SelectItem value="failed">Failed</SelectItem>
                  <SelectItem value="pending">Pending</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Type</TableHead>
                  <TableHead>Target</TableHead>
                  <TableHead>Content</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Time</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredActivities.map((activity) => (
                  <TableRow key={activity.id}>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        {activity.type === "like" && <Heart className="h-4 w-4 text-pink-500" />}
                        {activity.type === "follow" && <UserPlus className="h-4 w-4 text-violet-500" />}
                        {activity.type === "comment" && <MessageCircle className="h-4 w-4 text-blue-500" />}
                        {activity.type === "post" && <ImageIcon className="h-4 w-4 text-green-500" />}
                        {activity.type === "share" && <Share2 className="h-4 w-4 text-orange-500" />}
                        {activity.type === "dm" && <Mail className="h-4 w-4 text-cyan-500" />}
                        <span className="capitalize">{activity.type}</span>
                      </div>
                    </TableCell>
                    <TableCell>{activity.target}</TableCell>
                    <TableCell>{activity.targetContent}</TableCell>
                    <TableCell>
                      {activity.status === "success" && (
                        <Badge
                          variant="outline"
                          className="bg-green-50 text-green-700 border-green-200 dark:bg-green-900 dark:text-green-300 dark:border-green-800"
                        >
                          <CheckCircle2 className="h-3 w-3 mr-1" /> Success
                        </Badge>
                      )}
                      {activity.status === "failed" && (
                        <Badge
                          variant="outline"
                          className="bg-red-50 text-red-700 border-red-200 dark:bg-red-900 dark:text-red-300 dark:border-red-800"
                        >
                          <XCircle className="h-3 w-3 mr-1" /> Failed
                        </Badge>
                      )}
                      {activity.status === "pending" && (
                        <Badge
                          variant="outline"
                          className="bg-yellow-50 text-yellow-700 border-yellow-200 dark:bg-yellow-900 dark:text-yellow-300 dark:border-yellow-800"
                        >
                          <Clock className="h-3 w-3 mr-1" /> Pending
                        </Badge>
                      )}
                    </TableCell>
                    <TableCell>{activity.time}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>

            <div className="flex items-center justify-between mt-4">
              <div className="text-sm text-muted-foreground">
                Showing {filteredActivities.length} of {allActivities.length} activities
              </div>
              <div className="flex items-center gap-2">
                <Button variant="outline" size="sm" disabled>
                  Previous
                </Button>
                <Button variant="outline" size="sm">
                  Next
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </main>
    </div>
  )
}
