"use client"

import type React from "react"

import { useEffect, useState } from "react"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"
import { toast } from "sonner"
import { Upload } from "lucide-react"
import Image from "next/image"
import { TourismObject } from "@/types/types"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { useRouter } from "next/navigation"
import { getTourismObjectsList } from "@/app/api/bot"

const LLM_API = process.env.NEXT_PUBLIC_LLM_API_BASE_URL
const API = process.env.NEXT_PUBLIC_API_BASE_URL

export default function SchedulePostPage() {
  const router = useRouter();
  const [imagePreview, setImagePreview] = useState<string | null>(null)
  const [isUploading, setIsUploading] = useState(false)
  const [uploadedImageUrl, setUploadedImageUrl] = useState<string | null>(null)
  const [keywords, setKeywords] = useState<string>("")
  const [imageDescription, setImageDescription] = useState<string>("")
  const [additionalContext, setAdditionalContext] = useState<string>("")
  const [generatedCaption, setGeneratedCaption] = useState<string>("")
  const [isGenerating, setIsGenerating] = useState(false)
  const [isScheduling, setIsScheduling] = useState(false)

  // Tourism object selection
  const [tourismObjects, setTourismObjects] = useState<TourismObject[]>([]);
  const [selectedTourismObject, setSelectedTourismObject] = useState<string>("");
  const [loadingTourismObjects, setLoadingTourismObjects] = useState(false);

  // Fetch tourism objects on component mount
  useEffect(() => {
    const fetchTourismObjects = async () => {
      setLoadingTourismObjects(true);
      try {
        const data = await getTourismObjectsList();
        setTourismObjects(data);
      } catch (error) {
        console.error('Failed to fetch tourism objects:', error);
        toast.error("Failed to load tourism objects.");
      } finally {
        setLoadingTourismObjects(false);
      }
    };

    fetchTourismObjects();
  }, []);

  const handleImageChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      // Upload image immediately
      await uploadImage(file)
    }
  }

  const uploadImage = async (file: File) => {
    setIsUploading(true)
    try {
      const formData = new FormData()
      formData.append('file', file)

      const response = await fetch('/api/upload', {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        throw new Error('Upload failed')
      }

      const data = await response.json()
      console.log('Cloudinary response:', data)
      
      setImagePreview(data.url)
      setUploadedImageUrl(data.url) 
      toast.success("Image uploaded successfully")
    } catch (error) {
      console.error('Upload error:', error)
      toast.error("Failed to upload image")
    } finally {
      setIsUploading(false)
    }
  }

  const handleGenerateCaption = async () => {
    setIsGenerating(true)
    try {
      const requestBody = {
        image_description: imageDescription,
        caption_keywords: keywords.split(',').map(keyword => keyword.trim()).filter(keyword => keyword),
        additional_context: additionalContext
      }

      const response = await fetch(`${LLM_API}/caption`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      })

      if (!response.ok) {
        throw new Error(`Caption generation failed: ${response.statusText}`)
      }

      const data = await response.json()
      setGeneratedCaption(data.response)
      toast.success("Caption generated successfully")
    } catch (error) {
      console.error('Generation error:', error)
      toast.error("Failed to generate caption")
    } finally {
      setIsGenerating(false)
    }
  }

  const handleSchedulePost = async () => {
    if (!uploadedImageUrl) {
      toast.error("Please upload an image")
      return
    }

    if (!generatedCaption.trim()) {
      toast.error("Please generate a caption first")
      return
    }

    setIsScheduling(true)
    try {
      // Step 1: Hit LLM_API/post to get scheduling recommendation
      const llmRequestBody = {
        image_url: uploadedImageUrl,
        caption_message: generatedCaption,
      }

      toast.info("Getting optimal posting time...")
      const llmResponse = await fetch(`${LLM_API}/post`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(llmRequestBody),
      })

      if (!llmResponse.ok) {
        throw new Error(`LLM API failed: ${llmResponse.statusText}`)
      }

      const llmData = await llmResponse.json()
      console.log('LLM response:', llmData)

      // Step 2: Store in database using Django API
      const token = localStorage.getItem("jwtToken");
      if (!token) {
        toast.error("Please login first")
        return
      }
      let scheduledTime = llmData.scheduled_time;
      if (scheduledTime.includes(' ')) {
        scheduledTime = scheduledTime.replace(' ', 'T');
      }
      
      // Add timezone if not present
      if (!scheduledTime.includes('+') && !scheduledTime.includes('Z')) {
        scheduledTime = `${scheduledTime}+07:00`;
      }

      const scheduleRequestBody = {
        image_url: uploadedImageUrl,
        caption: generatedCaption,
        reason: llmData.reason,
        scheduled_time: scheduledTime,
        tourism_object_id: parseInt(selectedTourismObject)
      }

      toast.info("Saving to database...")
      const scheduleResponse = await fetch(`${API}/schedule-post/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(scheduleRequestBody),
      })

      if (!scheduleResponse.ok) {
        const errorData = await scheduleResponse.json()
        throw new Error(errorData.message || `Schedule API failed: ${scheduleResponse.statusText}`)
      }
      const scheduleData = await scheduleResponse.json()
      console.log('Schedule response:', scheduleData)
      
      const scheduledDate = new Date(llmData.scheduled_time);
      const formattedTime = scheduledDate.toLocaleString('en-US', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        timeZoneName: 'short'
      });
      
      toast.success(`Post scheduled successfully! It will be posted at ${formattedTime}`)
      // const scheduleData = await scheduleResponse.json()
      // console.log('Schedule response:', scheduleData)

      // // Step 3: Post directly to Instagram (for testing)
      // toast.info("Posting to Instagram...")
      // const postRequestBody = {
      //   image_path: uploadedImageUrl,
      //   caption: generatedCaption,
      //   tourism_object_id: parseInt(selectedTourismObject)
      // }

      // const postResponse = await fetch(`${API}/post/`, {
      //   method: 'POST',
      //   headers: {
      //     'Content-Type': 'application/json',
      //     'Authorization': `Bearer ${token}`
      //   },
      //   body: JSON.stringify(postRequestBody),
      // })

      // if (!postResponse.ok) {
      //   const errorData = await postResponse.json()
      //   console.warn('Instagram posting failed:', errorData)
      //   // Don't throw error here, just warn - the scheduling was successful
      //   toast.warning("Post scheduled successfully, but Instagram posting failed. Will retry later.")
      // } else {
      //   const postData = await postResponse.json()
      //   console.log('Instagram post response:', postData)
      //   toast.success("Post scheduled and posted to Instagram successfully!")
      // }
      // Reset form after successful scheduling
      setImagePreview(null)
      setUploadedImageUrl(null)
      setKeywords("")
      setImageDescription("")
      setAdditionalContext("")
      setGeneratedCaption("")
      setSelectedTourismObject("")
      
      router.push('/tourism');
    } catch (error) {
      console.error('Schedule error:', error)
      toast.error("Failed to schedule post")
    } finally {
      setIsScheduling(false)
    }
  }

  const handleRemoveImage = () => {
    setImagePreview(null)
    setUploadedImageUrl(null)
    setGeneratedCaption("")
  }

  return (
    <div className="container mx-auto py-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold">Schedule Post</h1>
        <p className="text-muted-foreground">Upload an image and add text for your scheduled post</p>
      </div>

      <div className="grid gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Upload Image</CardTitle>
            <CardDescription>Select an image for your post</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid gap-6">
              <div className="flex items-center justify-center">
                <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 w-full max-w-md flex flex-col items-center justify-center">
                  
                  {imagePreview ? (
                    <div className="relative w-full h-auto">
                      <Button
                        variant="destructive"
                        size="sm"
                        className="absolute top-0 right-2"
                        onClick={handleRemoveImage}
                      >
                        Remove
                      </Button>
                      <Image
                        src={imagePreview}
                        alt="Preview"
                        width={300}
                        height={300}
                        className="w-full h-auto rounded-md max-h-[300px] object-contain"
                      />
                      {isUploading && (
                        <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center rounded-md">
                          <div className="text-white text-sm">Uploading...</div>
                        </div>
                      )}
                    </div>
                  ) : (
                    <>
                      <Upload className="h-12 w-12 text-gray-400 mb-4" />
                      <p className="text-sm text-gray-500 mb-2">Drag and drop an image, or click to browse</p>
                      <Input
                        id="image-upload"
                        type="file"
                        accept="image/*"
                        className="hidden"
                        onChange={handleImageChange}
                      />
                        <Button variant="outline"
                          onClick={() => document.getElementById("image-upload")?.click()}
                          disabled={isUploading}
                        >
                        {isUploading ? "Uploading..." : "Select Image"}
                      </Button>
                    </>
                  )}
                </div>
              </div>
              {/* Tourism Object Selection */}
              <div className="space-y-2">
                <Label htmlFor="tourism-object">Tourism Object*</Label>
                <Select value={selectedTourismObject}
                  onValueChange={setSelectedTourismObject}
                  disabled={loadingTourismObjects}
                >
                  <SelectTrigger>
                    <SelectValue placeholder={loadingTourismObjects ? "Loading..." : "Select a tourism object to tag this post"} />
                  </SelectTrigger>
                  <SelectContent>
                    {tourismObjects.map((obj) => (
                      <SelectItem key={obj.id} value={obj.id.toString()}>
                        {obj.name} - {obj.object_type}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <p className="text-sm text-muted-foreground">
                  Tagging a tourism object helps track post performance for specific destinations or hotels.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Post Text</CardTitle>
            <CardDescription>Add text for your post</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid gap-6">
              <div className="space-y-2">
                <Label htmlFor="keywords-input">Keywords <span className="text-red-500">*</span></Label>
                <Input
                  id="keywords-input"
                  placeholder="travel, beach, sunset, vacation"
                  value={keywords}
                  onChange={(e) => setKeywords(e.target.value)}
                />
                <p className="text-sm text-muted-foreground">Enter keywords separated by commas</p>
              </div>

              <div className="space-y-2">
                <Label htmlFor="image-description-input">Image Description <span className="text-red-500">*</span></Label>
                <Textarea
                  id="image-description-input"
                  placeholder="Describe what's in the image..."
                  className="min-h-[120px]"
                  value={imageDescription}
                  onChange={(e) => setImageDescription(e.target.value)}
                />
                <p className="text-sm text-muted-foreground">Provide a detailed description of the image content</p>
              </div>

              <div className="space-y-2">
                <Label htmlFor="additional-context-input">Additional Context</Label>
                <Textarea
                  id="additional-context-input"
                  placeholder="Any additional context or information..."
                  className="min-h-[80px]"
                  value={additionalContext}
                  onChange={(e) => setAdditionalContext(e.target.value)}
                />
                <p className="text-sm text-muted-foreground">Optional: Add any extra context to help generate better captions</p>
              </div>

              {generatedCaption && (
                <div className="space-y-2">
                  <Label htmlFor="generated-caption">Generated Caption</Label>
                  <Textarea
                    id="generated-caption"
                    value={generatedCaption}
                    onChange={(e) => setGeneratedCaption(e.target.value)}
                    className="min-h-[100px]"
                    placeholder="Generated caption will appear here..."
                  />
                  <p className="text-sm text-muted-foreground">You can edit the generated caption before scheduling</p>
                </div>
              )}
            </div>
          </CardContent>
          <CardFooter>
            <Button 
              onClick={handleGenerateCaption} 
              className="ml-auto"
              disabled={isGenerating || isUploading || !keywords.trim() || !imageDescription.trim() || !selectedTourismObject.trim()}
            >
              {isGenerating ? "Generating..." : "Generate Caption"}
            </Button>
          </CardFooter>
        </Card>

        {/* Schedule Post Button Outside */}
        <div className="flex justify-end">
          <Button 
            onClick={handleSchedulePost} 
            size="lg"
            disabled={!uploadedImageUrl || !generatedCaption.trim() || isScheduling}
          >
            {isScheduling ? "Scheduling..." : "Schedule Post"}
          </Button>
        </div>
      </div>
    </div>
  )
}
