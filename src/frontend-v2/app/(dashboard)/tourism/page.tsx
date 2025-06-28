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
import { Search, MapPin, Star, TrendingUp, TrendingDown, Heart, MessageCircle, BarChart3 } from "lucide-react";
import { getTourismObjects } from "@/app/api/bot";
import { TourismObject, TourismObjectsResponse } from "@/types/types";
import { useRouter } from 'next/navigation';
import Image from "next/image";

export default function TourismPage() {
  const [tourismData, setTourismData] = useState<TourismObjectsResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [searchQuery, setSearchQuery] = useState("");
  const router = useRouter();

  const handleViewAnalytics = (objectId: number) => {
    router.push(`/tourism/analytics/${objectId}`);
  };

  useEffect(() => {
    const fetchTourismObjects = async () => {
      setLoading(true);
      setError("");
      setTourismData(null);
      try {
        const data = await getTourismObjects();
        
        setTourismData(data);
      } catch (err: any) {
        setError(err.message || "Failed to fetch tourism objects");
      }
      setLoading(false);
    };

    fetchTourismObjects();
    const intervalId = setInterval(fetchTourismObjects, 10 * 60 * 1000);

    return () => clearInterval(intervalId);
  }, []);

  const filterObjects = (objects: TourismObject[]) => {
    return objects.filter((obj) =>
      obj.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      obj.location.toLowerCase().includes(searchQuery.toLowerCase())
    );
  };

  const MetricCard = ({ 
    title, 
    value, 
    percentChange, 
    icon: Icon, 
    format = 'number' 
  }: { 
    title: string; 
    value: number; 
    percentChange?: number; 
    icon: React.ElementType; 
    format?: 'number' | 'percentage' 
  }) => (
    <div className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
      <div className="flex items-center space-x-2">
        <Icon className="h-4 w-4 text-muted-foreground" />
        <span className="text-sm font-medium">{title}</span>
      </div>
      <div className="text-right">
        <div className="font-semibold">
          {format === 'percentage' ? `${value}%` : value.toLocaleString()}
        </div>
        {percentChange !== undefined && (
          <div className={`text-xs flex items-center ${percentChange >= 0 ? 'text-green-600' : 'text-red-600'}`}>
            {percentChange >= 0 ? <TrendingUp className="h-3 w-3 mr-1" /> : <TrendingDown className="h-3 w-3 mr-1" />}
            {percentChange >= 0 ? '+' : ''}{percentChange}%
          </div>
        )}
      </div>
    </div>
  );

  const ObjectCard = ({ object }: { object: TourismObject }) => (
      <Card className="hover:shadow-lg transition-shadow">
          <div className="relative h-48 w-full">
            <Image
            src={`/tourism/${object.image_url}`}
            alt={object.name}
            fill
            className="object-cover"
            unoptimized
            />
            <div className="absolute top-2 left-2">
                <Badge variant={object.object_type === 'hotel' ? 'default' : 'primary'}>
                      {object.object_type.charAt(0).toUpperCase() + object.object_type.slice(1)}
                </Badge>
            </div>
            <div className="absolute top-2 right-2">
            <div className="flex items-center bg-white/90 dark:bg-gray-900/90 rounded-full px-2 py-1 text-sm">
                <Star className="h-3 w-3 mr-1 fill-yellow-400 text-yellow-400" />
                {object.rating}
            </div>
            </div>
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
            value={object.metrics.total_posts}
            icon={BarChart3}
          />
          <MetricCard
            title="Likes"
            value={object.metrics.total_likes}
            percentChange={object.metrics.likes_percent_increase}
            icon={Heart}
          />
          <MetricCard
            title="Comments"
            value={object.metrics.total_comments}
            percentChange={object.metrics.comments_percent_increase}
            icon={MessageCircle}
          />
        </div>
      </CardContent>
    </Card>
  );

  return (
    <div className="flex flex-col min-h-screen">
      <Navbar title="Tourism Dashboard" />
      <main className="flex-1 p-6 space-y-6">
        <Card>
          <CardHeader>
            <CardTitle>Tourism Objects Dashboard</CardTitle>
            <CardDescription>
              Monitor engagement metrics for hotels and destinations
            </CardDescription>
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
                    <div className="text-2xl font-bold">
                      {Math.round(
                        [...tourismData.hotels, ...tourismData.destinations]
                          .reduce((sum, obj) => sum + obj.metrics.likes_percent_increase, 0) / 
                        tourismData.total_count
                      )}%
                    </div>
                    <div className="text-sm text-muted-foreground">Avg Likes Growth</div>
                  </div>
                </Card>
                <Card className="p-4">
                  <div className="text-center">
                    <div className="text-2xl font-bold">
                      {Math.round(
                        [...tourismData.hotels, ...tourismData.destinations]
                          .reduce((sum, obj) => sum + obj.metrics.comments_percent_increase, 0) / 
                        tourismData.total_count
                      )}%
                    </div>
                    <div className="text-sm text-muted-foreground">Avg Comments Growth</div>
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