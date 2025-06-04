"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Slider } from "@/components/ui/slider"
import { toast } from "sonner"
import { ConfigData } from "@/types/types"

const API = process.env.NEXT_PUBLIC_API_BASE_URL;

export default function ConfigPage() {
  const [temperature, setTemperature] = useState<number>(0.3)
  const [topK, setTopK] = useState<number>(10)
  const [maxToken, setMaxToken] = useState<number>(4096)
  const [maxIteration, setMaxIteration] = useState<number>(10)
  const [loading, setLoading] = useState<boolean>(true)
  const [saving, setSaving] = useState<boolean>(false)

  useEffect(() => {
    loadConfiguration()
  }, [])

  const loadConfiguration = async () => {
    try {
      const token = localStorage.getItem('jwtToken')
      if (!token) {
        toast.error("Please login first")
        return
      }

      const response = await fetch(`${API}/config/`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      })
      console.log('Response status:', response)

      if (response.ok) {
        const result = await response.json()
        const data: ConfigData = result.data

        setTemperature(data.temperature)
        setTopK(data.top_k)
        setMaxToken(data.max_token)
        setMaxIteration(data.max_iteration)
      } else {
        toast.error("Failed to load configuration")
      }
    } catch (error) {
      console.error('Error loading configuration:', error)
      toast.error("Error loading configuration")
    } finally {
      setLoading(false)
    }
  }

  const handleSave = async () => {
    setSaving(true)
    try {
      const token = localStorage.getItem('jwtToken')
      if (!token) {
        toast.error("Please login first")
        return
      }

      const configData: ConfigData = {
        temperature: temperature,
        top_k: topK,
        max_token: maxToken,
        max_iteration: maxIteration,
      }

      const response = await fetch(`${API}/config/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(configData),
      })

      const result = await response.json()

      if (response.ok) {
        toast.success("Configuration saved successfully")
      } else {
        toast.error(result.message || "Failed to save configuration")
      }
    } catch (error) {
      console.error('Error saving configuration:', error)
      toast.error("Error saving configuration")
    } finally {
      setSaving(false)
    }
  }

  if (loading) {
    return (
      <div className="container mx-auto py-6">
        <div className="flex items-center justify-center h-64">
          <div className="text-lg">Loading configuration...</div>
        </div>
      </div>
    )
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
              <span className="text-sm text-muted-foreground">Default: 10</span>
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
              <span className="text-sm text-muted-foreground">Default: 4096</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Max Iterations</CardTitle>
            <CardDescription>
              The maximum number of iterations for the model to generate a response
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex items-center space-x-4">
              <Input
                type="number"
                value={maxIteration}
                onChange={(e) => setMaxToken(Number(e.target.value))}
                min={1}
                max={10}
                className="w-24"
              />
              <span className="text-sm text-muted-foreground">Default: 10</span>
            </div>
          </CardContent>
        </Card>

        <div className="flex justify-end">
          <Button onClick={handleSave} disabled={saving}>
            {saving ? "Saving..." : "Save Configuration"}
          </Button>
        </div>
      </div>
    </div>
  )
}
