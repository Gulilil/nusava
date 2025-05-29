"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Button } from "@/components/ui/button"
import { Slider } from "@/components/ui/slider"
import { toast } from "sonner"

export default function ConfigPage() {
  const [systemPrompt, setSystemPrompt] = useState<string>(
    "This is like a text message for the initialization model. This text message can be a bit large, maybe a few sentences like that",
  )
  const [style, setStyle] = useState<string>("a Tourism Influencer in Social Media")
  const [temperature, setTemperature] = useState<number>(0.3)
  const [topK, setTopK] = useState<number>(5)
  const [maxToken, setMaxToken] = useState<number>(512)

  const handleSave = () => {
    // Here you would typically save the configuration to your backend
    // For now, we'll just show a success toast
    toast.success("Configuration saved successfully")
  }

  return (
    <div className="container mx-auto py-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold">Configuration</h1>
        <p className="text-muted-foreground">Adjust your AI model settings</p>
      </div>

      <div className="grid gap-6">
        <Card>
          <CardHeader>
            <CardTitle>System Prompt</CardTitle>
            <CardDescription>
              This is like a text message for the initialization model. This text message can be a bit large.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Textarea
              value={systemPrompt}
              onChange={(e) => setSystemPrompt(e.target.value)}
              placeholder="Enter system prompt"
              className="min-h-[120px]"
            />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Style</CardTitle>
            <CardDescription>Set the style for the model responses</CardDescription>
          </CardHeader>
          <CardContent>
            <Input
              value={style}
              onChange={(e) => setStyle(e.target.value)}
              placeholder="e.g., a Tourism Influencer in Social Media"
            />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Temperature</CardTitle>
            <CardDescription>
              Controls randomness: Lower values are more deterministic, higher values are more creative (Range: 0-1)
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <Slider
                value={[temperature]}
                min={0}
                max={1}
                step={0.01}
                onValueChange={(value) => setTemperature(value[0])}
              />
              <div className="flex justify-between">
                <span className="text-sm text-muted-foreground">0</span>
                <span className="text-sm font-medium">{temperature.toFixed(2)}</span>
                <span className="text-sm text-muted-foreground">1</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Top K</CardTitle>
            <CardDescription>Limits the next token selection to the K most probable tokens</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex items-center space-x-4">
              <Input
                type="number"
                value={topK}
                onChange={(e) => setTopK(Number(e.target.value))}
                min={1}
                max={100}
                className="w-24"
              />
              <span className="text-sm text-muted-foreground">Default: 5</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Max Tokens</CardTitle>
            <CardDescription>The maximum number of tokens that can be generated in the response</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex items-center space-x-4">
              <Input
                type="number"
                value={maxToken}
                onChange={(e) => setMaxToken(Number(e.target.value))}
                min={1}
                max={4096}
                className="w-24"
              />
              <span className="text-sm text-muted-foreground">Default: 512</span>
            </div>
          </CardContent>
        </Card>

        <div className="flex justify-end">
          <Button onClick={handleSave}>Save Configuration</Button>
        </div>
      </div>
    </div>
  )
}
