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
  const [image, setImage] = useState<File | null>(null)
  const [imagePreview, setImagePreview] = useState<string | null>(null)
  const [textType, setTextType] = useState<"keywords" | "caption">("keywords")
  const [text, setText] = useState<string>("")

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      setImage(file)
      const reader = new FileReader()
      reader.onloadend = () => {
        setImagePreview(reader.result as string)
      }
      reader.readAsDataURL(file)
    }
  }

  const handleSubmit = () => {
    if (!image) {
      toast.error("Please select an image")
      return
    }

    if (!text.trim()) {
      toast.error(`Please enter ${textType === "keywords" ? "keywords" : "a caption"}`)
      return
    }

    // Here you would typically send the data to your backend
    toast.success("Post scheduled successfully")
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
                    <div className="relative w-full">
                      <Image
                        src={imagePreview || "/placeholder.svg"}
                        alt="Preview"
                        fill
                        className="w-full h-auto rounded-md max-h-[300px] object-contain"
                      />
                      <Button
                        variant="destructive"
                        size="sm"
                        className="absolute top-2 right-2"
                        onClick={() => {
                          setImage(null)
                          setImagePreview(null)
                        }}
                      >
                        Remove
                      </Button>
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
                      <Button variant="outline" onClick={() => document.getElementById("image-upload")?.click()}>
                        Select Image
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
            </div>
          </CardContent>
          <CardFooter>
            <Button onClick={handleSubmit} className="ml-auto">
              Schedule Post
            </Button>
          </CardFooter>
        </Card>
      </div>
    </div>
  )
}
