"use client";

import React, { useState } from "react";
import { Navbar } from "@/components/navbar";
import { Card, CardHeader, CardContent, CardFooter, CardTitle, CardDescription } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { toast } from 'sonner';

import { Heart, UserPlus, MessageCircle, ImageIcon, Share2, Search, Send } from "lucide-react";

import { likePost, followUser, commentPost, postPhoto, sharePost } from "@/app/api/bot";

export default function ActionsPage() {
  // Like
  const [likeUrl, setLikeUrl] = useState("");
  const [likeLoading, setLikeLoading] = useState(false);

  // Follow
  const [followUsername, setFollowUsername] = useState("");
  const [followLoading, setFollowLoading] = useState(false);

  // Comment
  const [commentUrl, setCommentUrl] = useState("");
  const [commentText, setCommentText] = useState("");
  const [commentLoading, setCommentLoading] = useState(false);

  // Post
  const [postImage, setPostImage] = useState<File | null>(null);
  const [postCaption, setPostCaption] = useState("");const [postLoading, setPostLoading] = useState(false);
  const [previewUrl, setPreviewUrl] = useState("");

  // Share
  const [shareUrl, setShareUrl] = useState("");
  const [shareTo, setShareTo] = useState("");
  const [shareLoading, setShareLoading] = useState(false);

  // --- Handlers ---
  const handleLike = async () => {
    setLikeLoading(true);
    try {
      const res = await likePost(likeUrl);
      toast.success(res.data.message || "Post liked!");
    } catch (e: any) {
      toast.error(e.response?.data?.error || "Error occurred.");
    }
    setLikeLoading(false);
  };

  const handleFollow = async () => {
    setFollowLoading(true);
    try {
      const res = await followUser(followUsername.replace(/^@/, ""));
      toast.success(res.data.message || "User followed!");
    } catch (e: any) {
      toast.error(e.response?.data?.error || "Error occurred.");
    }
    setFollowLoading(false);
  };

  const handleComment = async () => {
    setCommentLoading(true);
    try {
      const res = await commentPost(commentUrl, commentText);
      toast.success(res.data.message || "Comment posted!");
    } catch (e: any) {
      toast.error(e.response?.data?.error || "Error occurred.");
    }
    setCommentLoading(false);
  };

  const handlePost = async () => {
    if (!postImage) return toast.error("Please upload an image!");
    setPostLoading(true); 
    try {
      const res = await postPhoto(previewUrl, postCaption);
      toast.success(res.data.message || "Post created!");
    } catch (e: any) {
      toast.success(e.response?.data?.error || "Error occurred.");
    }
    setPostLoading(false);
  };

  const handleShare = async () => {
    setShareLoading(true);
    const usernames = shareTo.split(",").map((u) => u.trim().replace(/^@/, "")).filter(Boolean);
    try {
      const res = await sharePost(shareUrl, usernames);
      toast.success(res.data.message || "Post shared!");
    } catch (e: any) {
      toast.error(e.response?.data?.error || "Error occurred.");
    }
    setShareLoading(false);
  };

  // --- File preview for Post tab ---
  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setPostImage(e.target.files[0]);
      setPreviewUrl(URL.createObjectURL(e.target.files[0]));
    }
  };

  // --- UI ---
  return (
    <div className="flex flex-col min-h-screen">
      <Navbar title="Manual Actions" />
      <main className="flex-1 p-6 space-y-6">
        <Tabs defaultValue="like" className="space-y-4">
          <TabsList className="grid w-full grid-cols-5">
            <TabsTrigger value="like"><Heart className="h-4 w-4" /> Like</TabsTrigger>
            <TabsTrigger value="follow"><UserPlus className="h-4 w-4" /> Follow</TabsTrigger>
            <TabsTrigger value="comment"><MessageCircle className="h-4 w-4" /> Comment</TabsTrigger>
            <TabsTrigger value="post"><ImageIcon className="h-4 w-4" /> Post</TabsTrigger>
            <TabsTrigger value="share"><Share2 className="h-4 w-4" /> Share</TabsTrigger>
          </TabsList>

          {/* Like */}
          <TabsContent value="like">
            <Card>
              <CardHeader>
                <CardTitle>Like a Post</CardTitle>
                <CardDescription>Manually like a post on Instagram</CardDescription>
              </CardHeader>
              <CardContent>
                <Label htmlFor="like-url">Media URL</Label>
                <Input id="like-url" value={likeUrl} onChange={e => setLikeUrl(e.target.value)} placeholder="https://www.instagram.com/p/..." />
              </CardContent>
              <CardFooter>
                <Button className="ml-auto" onClick={handleLike} disabled={likeLoading || !likeUrl}>
                  <Heart className="mr-2 h-4 w-4" />
                  {likeLoading ? "Liking..." : "Like Post"}
                </Button>
              </CardFooter>
            </Card>
          </TabsContent>

          {/* Follow */}
          <TabsContent value="follow">
            <Card>
              <CardHeader>
                <CardTitle>Follow a User</CardTitle>
                <CardDescription>Manually follow an Instagram user</CardDescription>
              </CardHeader>
              <CardContent>
                <Label htmlFor="follow-username">Account Username</Label>
                <Input id="follow-username" value={followUsername} onChange={e => setFollowUsername(e.target.value)} placeholder="@username" />
              </CardContent>
              <CardFooter>
                <Button className="ml-auto" onClick={handleFollow} disabled={followLoading || !followUsername}>
                  <UserPlus className="mr-2 h-4 w-4" />
                  {followLoading ? "Following..." : "Follow User"}
                </Button>
              </CardFooter>
            </Card>
          </TabsContent>

          {/* Comment */}
          <TabsContent value="comment">
            <Card>
              <CardHeader>
                <CardTitle>Comment on a Post</CardTitle>
                <CardDescription>Manually comment on an Instagram post</CardDescription>
              </CardHeader>
              <CardContent>
                <Label htmlFor="comment-url">Media URL</Label>
                <Input id="comment-url" value={commentUrl} onChange={e => setCommentUrl(e.target.value)} placeholder="https://www.instagram.com/p/..." />
                <Label htmlFor="comment-text" className="mt-2">Comment</Label>
                <Textarea id="comment-text" value={commentText} onChange={e => setCommentText(e.target.value)} placeholder="Write your comment here..." />
              </CardContent>
              <CardFooter>
                <Button className="ml-auto" onClick={handleComment} disabled={commentLoading || !commentUrl || !commentText}>
                  <MessageCircle className="mr-2 h-4 w-4" />
                  {commentLoading ? "Commenting..." : "Post Comment"}
                </Button>
              </CardFooter>
            </Card>
          </TabsContent>

          {/* Post */}
          <TabsContent value="post">
            <Card>
              <CardHeader>
                <CardTitle>Create a Post</CardTitle>
                <CardDescription>Manually create an Instagram post</CardDescription>
              </CardHeader>
              <CardContent>
                <Label htmlFor="post-image">Upload Image</Label>
                <Input id="post-image" type="file" accept="image/*" onChange={handleImageChange} />
                {previewUrl && <img src={previewUrl} alt="Preview" className="my-2 h-32 rounded-lg" />}
                <Label htmlFor="post-caption" className="mt-2">Caption</Label>
                <Textarea id="post-caption" value={postCaption} onChange={e => setPostCaption(e.target.value)} placeholder="Write your caption here..." />
              </CardContent>
              <CardFooter>
                <Button className="ml-auto" onClick={handlePost} disabled={postLoading || !postImage || !postCaption}>
                  <ImageIcon className="mr-2 h-4 w-4" />
                  {postLoading ? "Posting..." : "Create Post"}
                </Button>
              </CardFooter>
            </Card>
          </TabsContent>

          {/* Share */}
          <TabsContent value="share">
            <Card>
              <CardHeader>
                <CardTitle>Share a Post</CardTitle>
                <CardDescription>Manually share an Instagram post</CardDescription>
              </CardHeader>
              <CardContent>
                <Label htmlFor="share-url">Media URL to Share</Label>
                <Input id="share-url" value={shareUrl} onChange={e => setShareUrl(e.target.value)} placeholder="https://www.instagram.com/p/..." />
                <Label htmlFor="share-to" className="mt-2">Accounts to Share With (comma separated)</Label>
                <Input id="share-to" value={shareTo} onChange={e => setShareTo(e.target.value)} placeholder="@user1, @user2" />
              </CardContent>
              <CardFooter>
                <Button className="ml-auto" onClick={handleShare} disabled={shareLoading || !shareUrl || !shareTo}>
                  <Share2 className="mr-2 h-4 w-4" />
                  {shareLoading ? "Sharing..." : "Share Post"}
                </Button>
              </CardFooter>
            </Card>
          </TabsContent>
        </Tabs>
         {/* Direct Messages Section */}
        <Card className="mt-6">
          <CardHeader>
            <CardTitle>Direct Messages</CardTitle>
            <CardDescription>Send and read direct messages</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-3 gap-4">
              {/* Message List */}
              <div className="col-span-1 border rounded-lg">
                <div className="p-3 border-b">
                  <div className="relative">
                    <Search className="absolute left-2 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                    <Input placeholder="Search conversations..." className="pl-8" />
                  </div>
                </div>
                <div className="h-[400px] overflow-auto">
                  <div className="p-3 border-b hover:bg-slate-50 cursor-pointer">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-full bg-slate-200"></div>
                      <div>
                        <p className="font-medium">@user1</p>
                        <p className="text-sm text-gray-500 truncate">Hey, how are you?</p>
                      </div>
                    </div>
                  </div>
                  <div className="p-3 border-b hover:bg-slate-50 cursor-pointer bg-slate-50">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-full bg-slate-200"></div>
                      <div>
                        <p className="font-medium">@user2</p>
                        <p className="text-sm text-gray-500 truncate">Check out this post!</p>
                      </div>
                    </div>
                  </div>
                  <div className="p-3 border-b hover:bg-slate-50 cursor-pointer">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-full bg-slate-200"></div>
                      <div>
                        <p className="font-medium">@user3</p>
                        <p className="text-sm text-gray-500 truncate">Thanks for the follow!</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Message Content */}
              <div className="col-span-2 border rounded-lg flex flex-col">
                <div className="p-3 border-b">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-slate-200"></div>
                    <p className="font-medium">@user2</p>
                  </div>
                </div>
                <div className="flex-1 p-3 overflow-auto h-[320px]">
                  <div className="flex flex-col gap-3">
                    <div className="flex items-start gap-2 max-w-[80%]">
                      <div className="w-8 h-8 rounded-full bg-slate-200 flex-shrink-0"></div>
                      <div className="bg-slate-100 p-3 rounded-lg">
                        <p>Hey there! How&apos;s it going?</p>
                        <p className="text-xs text-gray-500 mt-1">10:30 AM</p>
                      </div>
                    </div>
                    <div className="flex items-start gap-2 max-w-[80%] self-end">
                      <div className="bg-blue-100 p-3 rounded-lg">
                        <p>Hi! I&apos;m doing great, thanks for asking!</p>
                        <p className="text-xs text-gray-500 mt-1">10:32 AM</p>
                      </div>
                    </div>
                    <div className="flex items-start gap-2 max-w-[80%]">
                      <div className="w-8 h-8 rounded-full bg-slate-200 flex-shrink-0"></div>
                      <div className="bg-slate-100 p-3 rounded-lg">
                        <p>Check out this post! I think you&apos;ll like it.</p>
                        <p className="text-xs text-gray-500 mt-1">10:35 AM</p>
                      </div>
                    </div>
                  </div>
                </div>
                <div className="p-3 border-t">
                  <div className="flex gap-2">
                    <Textarea placeholder="Type a message..." className="min-h-[60px]" />
                    <Button className="flex-shrink-0">
                      <Send className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </main>
    </div>
  );
}
