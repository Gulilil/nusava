"use client"

import type React from "react"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import { Label } from "@/components/ui/label"
import { toast } from "sonner"
import { Upload } from "lucide-react"
import Image from "next/image"

export default function SchedulePostPage() {
  const [imagePreview, setImagePreview] = useState<string | null>(null)
  const [isUploading, setIsUploading] = useState(false)
  const [textType, setTextType] = useState<"keywords" | "caption">("keywords")
  const [text, setText] = useState<string>("")
  const [generatedCaption, setGeneratedCaption] = useState<string>("")
  const [isGenerating, setIsGenerating] = useState(false)

  const caption_url = "http://localhost:7000/caption"
      // Field format for caption JSON body: 
      // {
      //   image_description: str, 
      //   caption_keywords : list[str],
      //   additional_context: str (optional)
      // }
  const schedule_post_url = "http://localhost:7000/post"
      //  Field format for post JSON body: 
      // {
      //   image_url: str, 
      //   caption_message: str, 
      // }

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
      console.log(data.url)
      console.log(data.url && "/uploads/test.png")
      setImagePreview(data.url)
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
      // TODO: Replace with your actual backend endpoint for caption generation
      // const response = await fetch('/api/generate-caption', {
      //   method: 'POST',
      //   headers: {
      //     'Content-Type': 'application/json',
      //   },
      //   body: JSON.stringify({
      //     image_url: uploadedImageUrl,
      //     text_type: textType,
      //     text: text
      //   }),
      // })
      // const data = await response.json()
      // setGeneratedCaption(data.caption)

      // For now, simulate caption generation
      await new Promise(resolve => setTimeout(resolve, 2000)) // Simulate API call
      setGeneratedCaption(`Generated caption based on ${textType}: ${text}`)
      toast.success("Caption generated successfully")
    } catch (error) {
      console.error('Generation error:', error)
      toast.error("Failed to generate caption")
    } finally {
      setIsGenerating(false)
    }
  }

  const handleSchedulePost = async () => {
    if (!imagePreview) {
      toast.error("Please upload an image")
      return
    }

    if (!generatedCaption.trim()) {
      toast.error("Please generate a caption first")
      return
    }

    try {
      // TODO: Send to your Django backend for scheduling
      // const response = await fetch('/api/schedule-post', {
      //   method: 'POST',
      //   headers: {
      //     'Content-Type': 'application/json',
      //   },
      //   body: JSON.stringify({
      //     image_url: uploadedImageUrl,
      //     caption: generatedCaption,
      //     text_type: textType,
      //     original_text: text
      //   }),
      // })

      toast.success("Post scheduled successfully")
    } catch (error) {
      console.error('Schedule error:', error)
      toast.error("Failed to schedule post")
    }
  }

  const handleRemoveImage = () => {
    setImagePreview(null)
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
              <RadioGroup
                defaultValue="keywords"
                className="flex gap-4"
                onValueChange={(value) => setTextType(value as "keywords" | "caption")}
              >
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="keywords" id="keywords" />
                  <Label htmlFor="keywords">Keywords</Label>
                </div>
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="caption" id="caption" />
                  <Label htmlFor="caption">Image Description</Label>
                </div>
              </RadioGroup>

              {textType === "keywords" ? (
                <div className="space-y-2">
                  <Label htmlFor="keywords-input">Enter Keywords (comma separated)</Label>
                  <Input
                    id="keywords-input"
                    placeholder="travel, beach, sunset, vacation"
                    value={text}
                    onChange={(e) => setText(e.target.value)}
                  />
                </div>
              ) : (
                <div className="space-y-2">
                  <Label htmlFor="caption-input">Enter Image Description</Label>
                  <Textarea
                    id="caption-input"
                    placeholder="Write your image description here..."
                    className="min-h-[150px]"
                    value={text}
                    onChange={(e) => setText(e.target.value)}
                  />
                </div>
              )}

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
                </div>
              )}
            </div>
          </CardContent>
          <CardFooter>
            <Button 
              onClick={handleGenerateCaption} 
              className="ml-auto"
              disabled={isGenerating || isUploading}
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
            disabled={!imagePreview || !generatedCaption.trim()}
          >
            Schedule Post
          </Button>
        </div>
      </div>
    </div>
  )
}
