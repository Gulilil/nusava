"use client"
import { Navbar } from "@/components/navbar"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"
import { ArrowUpRight, Heart, MessageCircle, UserPlus, Clock, CheckCircle2, XCircle, ArrowRight, Settings } from "lucide-react"
import { useState } from "react"
import { Button } from "@/components/ui/button"
import Link from "next/link"

// Sample data
const recentActivities = [
  {
    id: 1,
    type: "like",
    target: "@fashionista",
    status: "success",
    time: "2 min ago",
  },
  {
    id: 2,
    type: "follow",
    target: "@travel_lover",
    status: "success",
    time: "5 min ago",
  },
  {
    id: 3,
    type: "comment",
    target: "@foodie_blog",
    status: "failed",
    time: "10 min ago",
  },
  {
    id: 4,
    type: "like",
    target: "@tech_news",
    status: "success",
    time: "15 min ago",
  },
  {
    id: 5,
    type: "follow",
    target: "@fitness_guru",
    status: "pending",
    time: "20 min ago",
  },
]

export default function Dashboard() {
  const [botConfig] = useState({
    systemPrompt: "This is like a text message for the initialization model...",
    style: "a Tourism Influencer in Social Media",
    temperature: 0.3,
    topK: 5,
    maxToken: 512,
  })

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
                            {activity.type === "like" && <Heart className="h-4 w-4 text-pink-500" />}
                            {activity.type === "follow" && <UserPlus className="h-4 w-4 text-violet-500" />}
                            {activity.type === "comment" && <MessageCircle className="h-4 w-4 text-blue-500" />}
                            <span className="capitalize">{activity.type}</span>
                          </div>
                        </TableCell>
                        <TableCell>{activity.target}</TableCell>
                        <TableCell>
                          {activity.status === "success" && (
                            <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200">
                              <CheckCircle2 className="h-3 w-3 mr-1" /> Success
                            </Badge>
                          )}
                          {activity.status === "failed" && (
                            <Badge variant="outline" className="bg-red-50 text-red-700 border-red-200">
                              <XCircle className="h-3 w-3 mr-1" /> Failed
                            </Badge>
                          )}
                          {activity.status === "pending" && (
                            <Badge variant="outline" className="bg-yellow-50 text-yellow-700 border-yellow-200">
                              <Clock className="h-3 w-3 mr-1" /> Pending
                            </Badge>
                          )}
                        </TableCell>
                        <TableCell>{activity.time}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
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
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                <div>
                  <h3 className="font-medium">Style</h3>
                  <p className="text-sm text-muted-foreground">{botConfig.style}</p>
                </div>
                <div>
                  <h3 className="font-medium">Temperature</h3>
                  <p className="text-sm text-muted-foreground">{botConfig.temperature} (Creativity level)</p>
                </div>
                <div>
                  <h3 className="font-medium">Top K</h3>
                  <p className="text-sm text-muted-foreground">{botConfig.topK} (Vector search limit)</p>
                </div>
                <div>
                  <h3 className="font-medium">Max Tokens</h3>
                  <p className="text-sm text-muted-foreground">{botConfig.maxToken} (Response length limit)</p>
                </div>
                <div className="md:col-span-2">
                  <h3 className="font-medium">System Prompt</h3>
                  <p className="text-sm text-muted-foreground truncate">{botConfig.systemPrompt}</p>
                </div>
              </div>
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
