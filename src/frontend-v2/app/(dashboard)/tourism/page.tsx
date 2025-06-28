/* eslint-disable @typescript-eslint/no-explicit-any */
"use client";

import { useState, useEffect } from "react";
import { Navbar } from "@/components/navbar";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Search, MapPin, Star, TrendingUp, TrendingDown, Heart, MessageCircle, BarChart3, RefreshCw, Calendar } from "lucide-react";
import { getTourismObjects, getAllTourismStatistics } from "@/app/api/bot";
import { TourismObject, TourismObjectsResponse, AllTourismStatistics } from "@/types/types";
import { useRouter } from 'next/navigation';
import Image from "next/image";

export default function TourismPage() {
  const [tourismData, setTourismData] = useState<TourismObjectsResponse | null>(null);
  const [tourismStats, setTourismStats] = useState<AllTourismStatistics | null>(null);
  const [loading, setLoading] = useState(false);
  const [statsLoading, setStatsLoading] = useState(false);
  const [error, setError] = useState("");
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedHours] = useState<number>(24);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const router = useRouter();

  const handleViewAnalytics = (objectId: number) => {
    router.push(`/tourism/analytics/${objectId}`);
  };

  // Fetch tourism objects (basic data)
  useEffect(() => {
    const fetchTourismObjects = async () => {
      setLoading(true);
      setError("");
      try {
        const data = await getTourismObjects();
        setTourismData(data);
      } catch (err: any) {
        setError(err.message || "Failed to fetch tourism objects");
      }
      setLoading(false);
    };

    fetchTourismObjects();
  }, []);

  // Fetch tourism statistics separately
  useEffect(() => {
    const fetchTourismStatistics = async () => {
      setStatsLoading(true);
      try {
        const data = await getAllTourismStatistics(selectedHours);
        setTourismStats(data);
        setLastUpdated(new Date());
      } catch (err: any) {
        console.error("Failed to fetch tourism statistics:", err);
        // Don't set error, just log it
      }
      setStatsLoading(false);
    };

    fetchTourismStatistics();
  }, [selectedHours]);

  const refreshStatistics = async () => {
    setStatsLoading(true);
    try {
      const data = await getAllTourismStatistics(selectedHours);
      setTourismStats(data);
      setLastUpdated(new Date());
    } catch (err: any) {
      console.error("Failed to refresh statistics:", err);
    }
    setStatsLoading(false);
  };

  const filterObjects = (objects: TourismObject[]) => {
    return objects.filter((obj) =>
      obj.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      obj.location.toLowerCase().includes(searchQuery.toLowerCase())
    );
  };

  // Helper function to get statistics for a specific tourism object
  const getObjectStats = (objectId: number) => {
    if (!tourismStats?.tourism_objects) return null;
    return tourismStats.tourism_objects.find(stats => stats.tourism_object.id === objectId);
  };

  const MetricCard = ({ 
    title, 
    value, 
    percentChange, 
    icon: Icon, 
    format = 'number',
    loading = false
  }: { 
    title: string; 
    value: number; 
    percentChange?: number; 
    icon: React.ElementType; 
    format?: 'number' | 'percentage';
    loading?: boolean;
  }) => (
    <div className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
      <div className="flex items-center space-x-2">
        <Icon className="h-4 w-4 text-muted-foreground" />
        <span className="text-sm font-medium">{title}</span>
      </div>
      <div className="text-right">
        {loading ? (
          <div className="h-4 w-12 bg-gray-300 dark:bg-gray-600 rounded animate-pulse"></div>
        ) : (
          <>
            <div className="font-semibold">
              {format === 'percentage' ? `${value}%` : value.toLocaleString()}
            </div>
            {percentChange !== undefined && (
              <div className={`text-xs flex items-center ${percentChange >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {percentChange >= 0 ? <TrendingUp className="h-3 w-3 mr-1" /> : <TrendingDown className="h-3 w-3 mr-1" />}
                {percentChange >= 0 ? '+' : ''}{percentChange.toFixed(2)}%
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );

  const ObjectCard = ({ object }: { object: TourismObject }) => {
    const stats = getObjectStats(object.id);
    const summary = stats?.summary;

    return (
      <Card className="hover:shadow-lg transition-shadow">
        <div className="relative h-48 w-full">
          <Image
            src={`/tourism/${object.image_url}`}
            alt={object.name}
            fill
            className="object-cover"
            onError={(e) => {
              (e.target as HTMLImageElement).src = '/tourism/default.jpg';
            }}
          />
          <div className="absolute top-2 left-2">
            <Badge variant={object.object_type === 'hotel' ? 'default' : 'secondary'}>
              {object.object_type.charAt(0).toUpperCase() + object.object_type.slice(1)}
            </Badge>
          </div>
          <div className="absolute top-2 right-2">
            <div className="flex items-center bg-white/90 dark:bg-gray-900/90 rounded-full px-2 py-1 text-sm">
              <Star className="h-3 w-3 mr-1 fill-yellow-400 text-yellow-400" />
              {object.rating}
            </div>
          </div>
          {summary && summary.total_posts > 0 && (
            <div className="absolute bottom-2 left-2">
              <Badge variant="outline" className="bg-white/90 dark:bg-gray-900/90">
                {summary.total_posts} posts
              </Badge>
            </div>
          )}
        </div>
        <CardHeader className="pb-3">
          <div className="flex justify-between items-start">
            <div className="flex-1">
              <CardTitle className="text-lg line-clamp-1">{object.name}</CardTitle>
              <div className="flex items-center text-sm text-muted-foreground mt-2">
                <MapPin className="h-3 w-3 mr-1" />
                <span className="line-clamp-1">{object.location}</span>
              </div>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={() => handleViewAnalytics(object.id)}
            >
              <BarChart3 className="h-4 w-4" />
            </Button>
          </div>
        </CardHeader>
        <CardContent className="pt-0">
          <div className="grid grid-cols-1 gap-2">
            <MetricCard
              title="Posts"
              value={summary?.total_posts || 0}
              icon={BarChart3}
              loading={statsLoading}
            />
            <MetricCard
              title="Likes"
              value={summary?.total_likes || 0}
              percentChange={summary?.likes_growth_rate}
              icon={Heart}
              loading={statsLoading}
            />
            <MetricCard
              title="Comments"
              value={summary?.total_comments || 0}
              percentChange={summary?.comments_growth_rate}
              icon={MessageCircle}
              loading={statsLoading}
            />
          </div>
          {summary && (
            <div className="mt-3 p-2 bg-blue-50 dark:bg-blue-900/20 rounded text-center">
              <div className="text-sm text-blue-700 dark:text-blue-300">
                Avg: {summary.average_likes.toFixed(1)} likes, {summary.average_comments.toFixed(1)} comments
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    );
  };

  // Calculate overall statistics
  const calculateOverallStats = () => {
    if (!tourismStats?.tourism_objects) return null;
    
    const totalPosts = tourismStats.tourism_objects.reduce((sum, obj) => sum + obj.summary.total_posts, 0);
    const totalLikes = tourismStats.tourism_objects.reduce((sum, obj) => sum + obj.summary.total_likes, 0);
    const totalComments = tourismStats.tourism_objects.reduce((sum, obj) => sum + obj.summary.total_comments, 0);
    const avgLikesGrowth = tourismStats.tourism_objects.length > 0 ? 
      tourismStats.tourism_objects.reduce((sum, obj) => sum + obj.summary.likes_growth_rate, 0) / tourismStats.tourism_objects.length : 0;
    const avgCommentsGrowth = tourismStats.tourism_objects.length > 0 ? 
      tourismStats.tourism_objects.reduce((sum, obj) => sum + obj.summary.comments_growth_rate, 0) / tourismStats.tourism_objects.length : 0;

    return {
      totalPosts,
      totalLikes,
      totalComments,
      avgLikesGrowth,
      avgCommentsGrowth
    };
  };

  const overallStats = calculateOverallStats();

  return (
    <div className="flex flex-col min-h-screen">
      <Navbar title="Tourism Dashboard" />
      <main className="flex-1 p-6 space-y-6">
        <Card>
          <CardHeader>
            <div className="flex justify-between items-start">
              <div>
                <CardTitle>Tourism Objects Dashboard</CardTitle>
                <CardDescription>
                  Monitor engagement metrics for hotels and destinations
                </CardDescription>
              </div>
              <div className="flex items-center space-x-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={refreshStatistics}
                  disabled={statsLoading}
                >
                  <RefreshCw className={`h-4 w-4 ${statsLoading ? 'animate-spin' : ''}`} />
                </Button>
              </div>
            </div>
            {lastUpdated && (
              <div className="flex items-center text-sm text-muted-foreground mt-2">
                <Calendar className="h-4 w-4 mr-1" />
                Last updated: {lastUpdated.toLocaleTimeString()}
              </div>
            )}
          </CardHeader>
          <CardContent className="space-y-4">
            {error && (
              <p className="text-red-600 font-semibold mb-2">{error}</p>
            )}

            {/* Summary Stats */}
            {tourismData && (
              <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-6">
                <Card className="p-4">
                  <div className="text-center">
                    <div className="text-2xl font-bold">{tourismData.total_count}</div>
                    <div className="text-sm text-muted-foreground">Total Objects</div>
                  </div>
                </Card>
                <Card className="p-4">
                  <div className="text-center">
                    <div className="text-2xl font-bold">{tourismData.hotels_count}</div>
                    <div className="text-sm text-muted-foreground">Hotels</div>
                  </div>
                </Card>
                <Card className="p-4">
                  <div className="text-center">
                    <div className="text-2xl font-bold">{tourismData.destinations_count}</div>
                    <div className="text-sm text-muted-foreground">Destinations</div>
                  </div>
                </Card>
                <Card className="p-4">
                  <div className="text-center">
                    {statsLoading ? (
                      <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded animate-pulse"></div>
                    ) : (
                      <>
                        <div className="text-2xl font-bold">
                          {overallStats ? `${overallStats.avgLikesGrowth.toFixed(1)}%` : 'N/A'}
                        </div>
                        <div className="text-sm text-muted-foreground">Avg Likes Growth</div>
                      </>
                    )}
                  </div>
                </Card>
                <Card className="p-4">
                  <div className="text-center">
                    {statsLoading ? (
                      <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded animate-pulse"></div>
                    ) : (
                      <>
                        <div className="text-2xl font-bold">
                          {overallStats ? `${overallStats.avgCommentsGrowth.toFixed(1)}%` : 'N/A'}
                        </div>
                        <div className="text-sm text-muted-foreground">Avg Comments Growth</div>
                      </>
                    )}
                  </div>
                </Card>
              </div>
            )}

            {/* Additional Statistics Cards */}
            {overallStats && (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                <Card className="p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <BarChart3 className="h-5 w-5 text-blue-600" />
                      <span className="font-medium">Total Posts</span>
                    </div>
                    <div className="text-xl font-bold">{overallStats.totalPosts}</div>
                  </div>
                </Card>
                <Card className="p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <Heart className="h-5 w-5 text-red-600" />
                      <span className="font-medium">Total Likes</span>
                    </div>
                    <div className="text-xl font-bold">{overallStats.totalLikes.toLocaleString()}</div>
                  </div>
                </Card>
                <Card className="p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <MessageCircle className="h-5 w-5 text-blue-600" />
                      <span className="font-medium">Total Comments</span>
                    </div>
                    <div className="text-xl font-bold">{overallStats.totalComments.toLocaleString()}</div>
                  </div>
                </Card>
              </div>
            )}

            {/* Search */}
            <div className="relative">
              <Search className="absolute left-2 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                placeholder="Search tourism objects..."
                className="pl-8"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>

            {loading && <p>Loading tourism objects...</p>}
            
            {!loading && tourismData && (
              <Tabs defaultValue="all" className="mt-6">
                <TabsList className="mb-4">
                  <TabsTrigger value="all">All Objects</TabsTrigger>
                  <TabsTrigger value="destinations">Destinations ({tourismData.destinations_count})</TabsTrigger>
                  <TabsTrigger value="hotels">Hotels ({tourismData.hotels_count})</TabsTrigger>
                </TabsList>

                <TabsContent value="all">
                  <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
                    {[...filterObjects(tourismData.destinations), ...filterObjects(tourismData.hotels)].map((object) => (
                      <ObjectCard key={object.id} object={object} />
                    ))}
                  </div>
                </TabsContent>

                <TabsContent value="hotels">
                  <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
                    {filterObjects(tourismData.hotels).map((hotel) => (
                      <ObjectCard key={hotel.id} object={hotel} />
                    ))}
                  </div>
                </TabsContent>

                <TabsContent value="destinations">
                  <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
                    {filterObjects(tourismData.destinations).map((destination) => (
                      <ObjectCard key={destination.id} object={destination} />
                    ))}
                  </div>
                </TabsContent>
              </Tabs>
            )}
            
            {!loading && !tourismData && <p>No tourism objects available.</p>}
          </CardContent>
        </Card>
      </main>
    </div>
  );
}