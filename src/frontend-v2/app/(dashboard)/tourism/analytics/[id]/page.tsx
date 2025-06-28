/* eslint-disable @typescript-eslint/no-explicit-any */
"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import Image from "next/image";
import { Navbar } from "@/components/navbar";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { 
  ArrowLeft, 
  MapPin, 
  Star, 
  Heart, 
  MessageCircle, 
  BarChart3, 
  TrendingUp, 
  TrendingDown,
  Eye,
  Calendar,
  ExternalLink
} from "lucide-react";
import { getTourismObjectDetail, getTourismObjectStatistics } from "@/app/api/bot";
import { TourismObject, TourismStatistics } from "@/types/types";
import { InstagramEmbed } from "@/components/instagram-embed";

export default function TourismAnalyticsPage() {
  const params = useParams();
  const router = useRouter();
  const [tourismObject, setTourismObject] = useState<TourismObject | null>(null);
  const [statistics, setStatistics] = useState<TourismStatistics | null>(null);
  const [loading, setLoading] = useState(true);
  const [statsLoading, setStatsLoading] = useState(false);
  const [error, setError] = useState("");
  const [selectedHours, setSelectedHours] = useState<number>(24);

  const objectId = parseInt(params.id as string);
    
  useEffect(() => {
    const fetchTourismDetails = async () => {
      if (!objectId) return;
      
      setLoading(true);
      setError("");
      try {
        const data = await getTourismObjectDetail(objectId);
        setTourismObject(data);
      } catch (err: any) {
        setError(err.message || "Failed to fetch tourism object details");
      }
      setLoading(false);
    };

    fetchTourismDetails();
  }, [objectId]);

  // Fetch statistics separately when days change
  useEffect(() => {
    const fetchStatistics = async () => {
      if (!objectId) return;
      
      setStatsLoading(true);
      try {
        const data = await getTourismObjectStatistics(objectId, selectedHours);
        setStatistics(data);
      } catch (err: any) {
        console.error("Failed to fetch statistics:", err);
        // Don't show error for statistics, just log it
      }
      setStatsLoading(false);
    };

    fetchStatistics();
  }, [objectId, selectedHours]);

  const MetricCard = ({ 
    title, 
    value, 
    percentChange, 
    icon: Icon, 
    format = 'number',
    description,
    color = 'blue'
  }: { 
    title: string; 
    value: number; 
    percentChange?: number; 
    icon: React.ElementType; 
    format?: 'number' | 'percentage';
    description?: string;
    color?: 'blue' | 'green' | 'purple' | 'orange';
  }) => {
    const colorClasses = {
      blue: 'bg-blue-50 dark:bg-blue-900/20 text-blue-600',
      green: 'bg-green-50 dark:bg-green-900/20 text-green-600',
      purple: 'bg-purple-50 dark:bg-purple-900/20 text-purple-600',
      orange: 'bg-orange-50 dark:bg-orange-900/20 text-orange-600'
    };

    return (
      <Card>
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className={`p-2 rounded-lg ${colorClasses[color]}`}>
                <Icon className="h-5 w-5" />
              </div>
              <div>
                <p className="text-sm font-medium">{title}</p>
                {description && (
                  <p className="text-xs text-muted-foreground">{description}</p>
                )}
              </div>
            </div>
            <div className="text-right">
              <div className="text-2xl font-bold">
                {format === 'percentage' ? `${value}%` : value.toLocaleString()}
              </div>
              {percentChange !== undefined && (
                <div className={`text-sm flex items-center justify-end ${percentChange >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {percentChange >= 0 ? <TrendingUp className="h-4 w-4 mr-1" /> : <TrendingDown className="h-4 w-4 mr-1" />}
                  {percentChange >= 0 ? '+' : ''}{percentChange.toFixed(2)}%
                </div>
              )}
            </div>
          </div>
        </CardContent>
      </Card>
    );
  };

  if (loading) {
    return (
      <div className="flex flex-col min-h-screen">
        <Navbar title="Tourism Analytics" />
        <main className="flex-1 p-6">
          <div className="flex items-center space-x-4 mb-6">
            <Button variant="outline" onClick={() => router.back()}>
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back
            </Button>
          </div>
          <p>Loading analytics...</p>
        </main>
      </div>
    );
  }

  if (error || !tourismObject) {
    return (
      <div className="flex flex-col min-h-screen">
        <Navbar title="Tourism Analytics" />
        <main className="flex-1 p-6">
          <div className="flex items-center space-x-4 mb-6">
            <Button variant="outline" onClick={() => router.back()}>
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back
            </Button>
          </div>
          <Card>
            <CardContent className="p-6">
              <p className="text-red-600">{error || "Tourism object not found"}</p>
            </CardContent>
          </Card>
        </main>
      </div>
    );
  }

  // Use real statistics if available, otherwise fallback to dummy data
  const summary = statistics?.summary || {
    total_posts: tourismObject.metrics?.total_posts || 0,
    total_likes: tourismObject.metrics?.total_likes || 0,
    total_comments: tourismObject.metrics?.total_comments || 0,
    average_likes: 0,
    average_comments: 0,
    likes_growth_rate: tourismObject.metrics?.likes_percent_increase || 0,
    comments_growth_rate: tourismObject.metrics?.comments_percent_increase || 0,
  };

  return (
    <div className="flex flex-col min-h-screen">
      <Navbar title="Tourism Analytics" />
      <main className="flex-1 p-6 space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Button variant="outline" onClick={() => router.back()}>
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Tourism
            </Button>
          </div>
          
          <div className="flex items-center space-x-2">
            <label className="text-sm font-medium">Period:</label>
            <Select value={selectedHours.toString()} onValueChange={(value) => setSelectedHours(parseInt(value))}>
              <SelectTrigger className="w-32">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="1">1 hour</SelectItem>
                <SelectItem value="6">6 hours</SelectItem>
                <SelectItem value="12">12 hours</SelectItem>
                <SelectItem value="24">1 Day</SelectItem>
                <SelectItem value="48">2 Days</SelectItem>
                <SelectItem value="72">3 Days</SelectItem>
                <SelectItem value="168">1 week</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        {/* Hero Section */}
        <Card className="overflow-hidden">
          <div className="relative h-64 w-full">
            <Image
              src={`/tourism/${tourismObject.image_url}`}
              alt={tourismObject.name}
              fill
              className="object-cover"
              onError={(e) => {
                (e.target as HTMLImageElement).src = '/tourism/default.jpg';
              }}
            />
            <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent" />
            <div className="absolute bottom-6 left-6 text-white">
              <div className="flex items-center space-x-2 mb-2">
                <Badge variant={tourismObject.object_type === 'hotel' ? 'default' : 'secondary'}>
                  {tourismObject.object_type.toUpperCase()}
                </Badge>
                <div className="flex items-center bg-white/20 rounded-full px-2 py-1">
                  <Star className="h-4 w-4 mr-1 fill-yellow-400 text-yellow-400" />
                  {tourismObject.rating}
                </div>
              </div>
              <h1 className="text-3xl font-bold mb-2">{tourismObject.name}</h1>
              <div className="flex items-center text-white/90">
                <MapPin className="h-4 w-4 mr-1" />
                {tourismObject.location}
              </div>
            </div>
          </div>
        </Card>

        {/* Key Metrics */}
        {statsLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[1, 2, 3, 4].map((i) => (
              <Card key={i} className="animate-pulse">
                <CardContent className="p-6">
                  <div className="h-20 bg-gray-200 dark:bg-gray-700 rounded"></div>
                </CardContent>
              </Card>
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <MetricCard
              title="Total Posts"
              value={summary.total_posts}
              icon={BarChart3}
              description="Content mentions across platforms"
              color="blue"
            />
            <MetricCard
              title="Total Likes"
              value={summary.total_likes}
              percentChange={summary.likes_growth_rate}
              icon={Heart}
              description="Engagement through likes"
              color="green"
            />
            <MetricCard
              title="Total Comments"
              value={summary.total_comments}
              percentChange={summary.comments_growth_rate}
              icon={MessageCircle}
              description="User interactions and feedback"
              color="purple"
            />
            <MetricCard
              title="Avg. Engagement"
              value={summary.average_likes + summary.average_comments}
              icon={Eye}
              description="Average interactions per post"
              color="orange"
            />
          </div>
        )}

        {/* Detailed Analytics */}
        <Tabs defaultValue="overview" className="space-y-6">
          <TabsList>
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="performance">Performance</TabsTrigger>
            <TabsTrigger value="posts">Instagram Posts</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Basic Information */}
              <Card>
                <CardHeader>
                  <CardTitle>Object Information</CardTitle>
                  <CardDescription>
                    Basic details about this tourism object
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-1 gap-4">
                    <div className="flex justify-between items-center p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                      <span className="text-sm font-medium">Name</span>
                      <span className="text-sm text-muted-foreground">{tourismObject.name}</span>
                    </div>
                    <div className="flex justify-between items-center p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                      <span className="text-sm font-medium">Type</span>
                      <span className="text-sm text-muted-foreground capitalize">{tourismObject.object_type}</span>
                    </div>
                    <div className="flex justify-between items-center p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                      <span className="text-sm font-medium">Location</span>
                      <span className="text-sm text-muted-foreground">{tourismObject.location}</span>
                    </div>
                    <div className="flex justify-between items-center p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                      <span className="text-sm font-medium">Rating</span>
                      <div className="flex items-center">
                        <Star className="h-4 w-4 mr-1 fill-yellow-400 text-yellow-400" />
                        <span className="text-sm text-muted-foreground">{tourismObject.rating}</span>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Statistics Summary */}
              <Card>
                <CardHeader>
                  <CardTitle>Statistics Summary</CardTitle>
                  <CardDescription>
                    Performance metrics for the last {selectedHours} hours
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {statsLoading ? (
                    <div className="space-y-4">
                      {[1, 2, 3].map((i) => (
                        <div key={i} className="h-12 bg-gray-200 dark:bg-gray-700 rounded animate-pulse"></div>
                      ))}
                    </div>
                  ) : (
                    <div className="space-y-4">
                      <div className="flex justify-between items-center p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                        <span className="text-sm font-medium text-blue-700 dark:text-blue-300">Avg. Likes per Post</span>
                        <span className="text-lg font-bold text-blue-700 dark:text-blue-300">
                          {summary.average_likes.toFixed(1)}
                        </span>
                      </div>
                      <div className="flex justify-between items-center p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
                        <span className="text-sm font-medium text-green-700 dark:text-green-300">Avg. Comments per Post</span>
                        <span className="text-lg font-bold text-green-700 dark:text-green-300">
                          {summary.average_comments.toFixed(1)}
                        </span>
                      </div>
                      <div className="flex justify-between items-center p-3 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
                        <span className="text-sm font-medium text-purple-700 dark:text-purple-300">Total Engagement</span>
                        <span className="text-lg font-bold text-purple-700 dark:text-purple-300">
                          {(summary.total_likes + summary.total_comments).toLocaleString()}
                        </span>
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="performance" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Performance Metrics</CardTitle>
                <CardDescription>
                  Detailed analysis of engagement performance over {selectedHours} hours
                </CardDescription>
              </CardHeader>
              <CardContent>
                {statsLoading ? (
                  <div className="h-40 bg-gray-200 dark:bg-gray-700 rounded animate-pulse"></div>
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="space-y-4">
                      <h3 className="text-lg font-semibold">Growth Analysis</h3>
                      <div className="space-y-3">
                        <div className="flex justify-between items-center p-4 border rounded-lg">
                          <div className="flex items-center space-x-3">
                            <Heart className="h-5 w-5 text-red-500" />
                            <span className="font-medium">Likes Growth</span>
                          </div>
                          <div className={`flex items-center ${summary.likes_growth_rate >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                            {summary.likes_growth_rate >= 0 ? 
                              <TrendingUp className="h-4 w-4 mr-1" /> : 
                              <TrendingDown className="h-4 w-4 mr-1" />
                            }
                            <span className="font-semibold">
                              {summary.likes_growth_rate >= 0 ? '+' : ''}{summary.likes_growth_rate.toFixed(2)}%
                            </span>
                          </div>
                        </div>
                        <div className="flex justify-between items-center p-4 border rounded-lg">
                          <div className="flex items-center space-x-3">
                            <MessageCircle className="h-5 w-5 text-blue-500" />
                            <span className="font-medium">Comments Growth</span>
                          </div>
                          <div className={`flex items-center ${summary.comments_growth_rate >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                            {summary.comments_growth_rate >= 0 ? 
                              <TrendingUp className="h-4 w-4 mr-1" /> : 
                              <TrendingDown className="h-4 w-4 mr-1" />
                            }
                            <span className="font-semibold">
                              {summary.comments_growth_rate >= 0 ? '+' : ''}{summary.comments_growth_rate.toFixed(2)}%
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>
                    
                    <div className="space-y-4">
                      <h3 className="text-lg font-semibold">Key Metrics</h3>
                      <div className="space-y-3">
                        <div className="text-center p-6 bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 rounded-lg">
                          <div className="text-3xl font-bold text-blue-600 mb-2">
                            {summary.total_posts}
                          </div>
                          <div className="text-sm text-blue-600 font-medium">Total Posts</div>
                        </div>
                        <div className="text-center p-6 bg-gradient-to-r from-green-50 to-blue-50 dark:from-green-900/20 dark:to-blue-900/20 rounded-lg">
                          <div className="text-3xl font-bold text-green-600 mb-2">
                            {tourismObject.rating}
                          </div>
                          <div className="text-sm text-green-600 font-medium">Object Rating</div>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="posts" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Instagram Posts</CardTitle>
                <CardDescription>
                  Posts tagged with this tourism object ({selectedHours} hours)
                </CardDescription>
              </CardHeader>
              <CardContent>
                {statsLoading ? (
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {[1, 2, 3].map((i) => (
                      <div key={i} className="h-96 bg-gray-200 dark:bg-gray-700 rounded animate-pulse"></div>
                    ))}
                  </div>
                ) : statistics?.posts && statistics.posts.length > 0 ? (
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {statistics.posts.map((post, index) => (
                      <Card key={index} className="overflow-hidden">
                        {/* Instagram Embed */}
                        <div className="flex justify-center items-center p-4 min-h-[500px]">
                          <div className="w-full max-w-[328px]">
                            <InstagramEmbed
                              permalink={`https://www.instagram.com/p/${post.shortcode}/`}
                            />
                          </div>
                        </div>
                        <div className="p-4 border-b">
                          <div className="flex items-center justify-between mb-2">
                            <div className="flex items-center space-x-2">
                              <Calendar className="h-4 w-4 text-muted-foreground" />
                              <span className="text-sm text-muted-foreground">
                                {new Date(post.posted_at).toLocaleDateString()}
                              </span>
                            </div>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => window.open(`https://www.instagram.com/p/${post.shortcode}/`, '_blank')}
                            >
                              <ExternalLink className="h-4 w-4" />
                            </Button>
                          </div>
                          
                          <div className="flex items-center justify-between text-sm mb-2">
                            <div className="flex items-center space-x-4">
                              <div className="flex items-center space-x-1">
                                <Heart className="h-4 w-4 text-red-500" />
                                <span>{post.likes.toLocaleString()}</span>
                                {post.likes_change !== 0 && (
                                  <span className={`text-xs ${post.likes_change > 0 ? 'text-green-600' : 'text-red-600'}`}>
                                    ({post.likes_change > 0 ? '+' : ''}{post.likes_change})
                                  </span>
                                )}
                              </div>
                              <div className="flex items-center space-x-1">
                                <MessageCircle className="h-4 w-4 text-blue-500" />
                                <span>{post.comments.toLocaleString()}</span>
                                {post.comments_change !== 0 && (
                                  <span className={`text-xs ${post.comments_change > 0 ? 'text-green-600' : 'text-red-600'}`}>
                                    ({post.comments_change > 0 ? '+' : ''}{post.comments_change})
                                  </span>
                                )}
                              </div>
                            </div>
                          </div>
                          
                          <p className="text-sm text-muted-foreground line-clamp-2">
                            {post.caption}
                          </p>
                        </div>
                        
                        
                      </Card>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-12">
                    <BarChart3 className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                    <h3 className="text-lg font-semibold mb-2">No posts found</h3>
                    <p className="text-muted-foreground mb-4">
                      No Instagram posts found for this tourism object in the last {selectedHours} hours.
                    </p>
                    <Button variant="outline" onClick={() => router.push('/tourism/add')}>
                      Create New Post
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
}