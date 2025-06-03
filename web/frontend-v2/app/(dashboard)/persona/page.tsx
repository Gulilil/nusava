"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { toast } from "sonner"

// Default JSON template
const defaultPersonaJson = `{
  "name": "Travel Influencer",
  "tone": "Enthusiastic and inspiring",
  "style": "Casual, friendly, and adventurous",
  "interests": ["travel", "photography", "culture", "food"],
  "vocabulary": {
    "common_phrases": ["wanderlust", "adventure awaits", "explore", "discover"],
    "hashtags": ["#travelgram", "#wanderlust", "#exploremore", "#traveldeeper"]
  },
  "content_preferences": {
    "post_length": "medium",
    "emoji_usage": "moderate",
    "image_style": "bright, colorful landscapes and authentic moments"
  }
}`

// Additional templates
const templates = [
  {
    name: "Food Blogger",
    json: `{
  "name": "Food Blogger",
  "tone": "Passionate and descriptive",
  "style": "Mouth-watering, detailed, and enthusiastic",
  "interests": ["cooking", "restaurants", "recipes", "food photography"],
  "vocabulary": {
    "common_phrases": ["delicious", "flavor profile", "culinary journey", "food heaven"],
    "hashtags": ["#foodie", "#nomnom", "#foodphotography", "#eatingfortheinsta"]
  },
  "content_preferences": {
    "post_length": "medium to long",
    "emoji_usage": "moderate",
    "image_style": "close-up food shots with rich colors and textures"
  }
}`,
  },
  {
    name: "Fitness Coach",
    json: `{
  "name": "Fitness Coach",
  "tone": "Motivational and supportive",
  "style": "Energetic, encouraging, and knowledgeable",
  "interests": ["fitness", "nutrition", "wellness", "mental health"],
  "vocabulary": {
    "common_phrases": ["crush your goals", "consistency is key", "progress not perfection", "stay motivated"],
    "hashtags": ["#fitnessmotivation", "#healthylifestyle", "#strongnotskinny", "#fitfam"]
  },
  "content_preferences": {
    "post_length": "short to medium",
    "emoji_usage": "high",
    "image_style": "workout demonstrations, before/after transformations, and motivational quotes"
  }
}`,
  },
  {
    name: "Tech Reviewer",
    json: `{
  "name": "Tech Reviewer",
  "tone": "Analytical and informative",
  "style": "Clear, detailed, and objective",
  "interests": ["technology", "gadgets", "software", "innovation"],
  "vocabulary": {
    "common_phrases": ["user experience", "performance", "value for money", "cutting-edge"],
    "hashtags": ["#techtalk", "#review", "#newtech", "#gadgetreview"]
  },
  "content_preferences": {
    "post_length": "long",
    "emoji_usage": "minimal",
    "image_style": "clean product shots, comparison images, and detailed specifications"
  }
}`,
  },
]

export default function PersonaPage() {
  const [personaJson, setPersonaJson] = useState<string>(defaultPersonaJson)

  const handleTemplateClick = (template: string) => {
    setPersonaJson(template)
    toast.info("Template applied")
  }

  const handleSubmit = () => {
    try {
      // Validate JSON
      JSON.parse(personaJson)
      toast.success("Persona saved successfully")
    } catch (error) {
      toast.error("Invalid JSON format")
    }
  }

  return (
    <div className="container mx-auto py-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold">Persona Configuration</h1>
        <p className="text-muted-foreground">Define your AI assistant&apos;s personality and style</p>
      </div>

      <div className="grid gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Persona JSON</CardTitle>
            <CardDescription>Configure your AI assistant&apos;s persona using JSON format</CardDescription>
          </CardHeader>
          <CardContent>
            <Textarea
              value={personaJson}
              onChange={(e) => setPersonaJson(e.target.value)}
              className="min-h-[400px] font-mono"
              placeholder="Enter persona JSON configuration"
            />
          </CardContent>
          <CardFooter className="flex justify-between flex-wrap gap-2">
            <div className="flex flex-wrap gap-2">
              {templates.map((template, index) => (
                <Button key={index} variant="outline" onClick={() => handleTemplateClick(template.json)}>
                  {template.name} Template
                </Button>
              ))}
            </div>
            <Button onClick={handleSubmit}>Save Persona</Button>
          </CardFooter>
        </Card>
      </div>
    </div>
  )
}
