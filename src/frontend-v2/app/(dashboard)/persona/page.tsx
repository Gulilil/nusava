"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { toast } from "sonner"
import { useRouter } from "next/navigation"
import Cookies from "js-cookie"
import axios from "axios"

// Default JSON template
const defaultPersonaJson = `{
  "age": 25,
  "style": "A very enthusiastic and inspiring person who speaks with passion about adventures. Uses vivid descriptions and always encourages others to explore new places. Has excellent command of language and speaks in an uplifting, motivational tone.",
  "occupation": "Travel Influencer"
}`

// Additional templates
const templates = [
  {
    name: "Luxury Travel Expert",
    json: `{
  "age": 35,
  "style": "A sophisticated and refined person who speaks with elegance about premium experiences. Uses luxurious and exclusive language, always highlighting the finest details. Sounds like someone who has impeccable taste and access to the best destinations.",
  "occupation": "Luxury Travel Consultant"
}`,
  },
  {
    name: "Budget Backpacker",
    json: `{
  "age": 23,
  "style": "A resourceful and energetic person who speaks with excitement about affordable travel hacks and budget-friendly destinations. Uses casual, relatable language and always shares money-saving tips. Sounds like someone who proves you don't need to be rich to see the world.",
  "occupation": "Budget Travel Blogger"
}`,
  },
  {
    name: "Cultural Explorer",
    json: `{
  "age": 40,
  "style": "A wise and curious person who speaks with deep respect for local cultures and traditions. Uses educational and thoughtful language, always emphasizing authentic experiences over tourist traps. Sounds like someone who truly understands and appreciates different cultures.",
  "occupation": "Cultural Anthropologist"
}`,
  },
  {
    name: "Family Travel Coordinator",
    json: `{
  "age": 32,
  "style": "A practical and caring person who speaks with warmth about family-friendly destinations and activities. Uses helpful and reassuring language, always considering safety and entertainment for all ages. Sounds like someone who knows how to make travel fun for everyone.",
  "occupation": "Family Travel Specialist"
}`,
  },
  {
    name: "Solo Wanderer",
    json: `{
  "age": 29,
  "style": "An independent and introspective person who speaks with confidence about solo travel experiences. Uses empowering and encouraging language, always promoting self-discovery through travel. Sounds like someone who finds strength and freedom in exploring alone.",
  "occupation": "Solo Travel Coach"
}`,
  },
  {
    name: "Eco-Conscious Traveler",
    json: `{
  "age": 31,
  "style": "An environmentally aware and responsible person who speaks passionately about sustainable travel practices. Uses mindful and eco-friendly language, always promoting destinations that respect nature and local communities. Sounds like someone who cares deeply about the planet.",
  "occupation": "Sustainable Tourism Advocate"
}`,
  },
]

const API = process.env.NEXT_PUBLIC_API_BASE_URL

export default function PersonaPage() {
  const router = useRouter()

  const [personaJson, setPersonaJson] = useState<string>("")
  const [originalPersonaJson, setOriginalPersonaJson] = useState<string>("")
  const [loading, setLoading] = useState<boolean>(true)
  const [saving, setSaving] = useState<boolean>(false)
  const handleUnauthorized = () => {
    Cookies.remove("auth")
    localStorage.removeItem("jwtToken")
    localStorage.removeItem("jwtRefresh")
    router.push("/login")
  }
  useEffect(() => {
    const fetchPersona = async () => {
      try {
        const token = localStorage.getItem('jwtToken')
        if (!token) return
        const response = await axios.get(`${API}/persona/`, {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        })

        if (response.status === 401) {
          handleUnauthorized()
          return
        }

        const personaData = response.data.data.persona
        console.log(personaData)
        if (personaData) {
          // If persona exists, format it as JSON string
          const formattedJson = JSON.stringify(personaData, null, 2)
          setPersonaJson(formattedJson)
          setOriginalPersonaJson(formattedJson)
        } else {
          // If no persona exists, use default template
          setPersonaJson(defaultPersonaJson)
          setOriginalPersonaJson("")
        }
      } catch (error) {
        if (axios.isAxiosError(error) && error.response?.status === 401) {
          handleUnauthorized()
          return
        }
        console.error("Error fetching persona:", error)
        toast.error("Error fetching persona")
        setPersonaJson(defaultPersonaJson)
      } finally {
        setLoading(false)
      }
    }

    fetchPersona()
  }, [router])

  const handleTemplateClick = (template: string) => {
    setPersonaJson(template)
    toast.info("Template applied")
  }

  const validatePersonaJson = (jsonString: string): boolean => {
    try {
      const parsed = JSON.parse(jsonString)

      if (!parsed.age || !parsed.style || !parsed.occupation) {
        return false
      }

      return true
    } catch (error) {
      console.log("Invalid JSON format:", error)
      return false
    }
  }

  const handleSubmit = async () => {
    if (!validatePersonaJson(personaJson)) {
      toast.error("Invalid JSON format or missing required fields (age, style, occupation)")
      return
    }

    setSaving(true)
    try {
      const token = localStorage.getItem('jwtToken')
      if (!token) return
      const response = await axios.post(`${API}/persona/`,
        {
          persona: JSON.parse(personaJson)
        },
        {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        }
      )
      if (response.status === 401) {
        handleUnauthorized()
        return
      }

      toast.success("Persona saved successfully")
      setOriginalPersonaJson(personaJson)
    } catch (error) {
      console.error("Error saving persona:", error)
      toast.error("Error saving persona")
    } finally {
      setSaving(false)
    }
  }

  // Check if save button should be disabled
  const isSaveDisabled = () => {
    if (saving || loading) return true
    if (!personaJson.trim()) return true
    if (personaJson === originalPersonaJson) return true
    if (!validatePersonaJson(personaJson)) return true
    return false
  }

  if (loading) {
    return (
      <div className="container mx-auto py-6">
        <div className="flex items-center justify-center h-64">
          <div className="text-lg">Loading persona...</div>
        </div>
      </div>
    )
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
            <CardDescription>
              Configure your AI assistant&apos;s persona using JSON format. Required fields: age, style, occupation
            </CardDescription>
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
                <Button
                  key={index}
                  variant="outline"
                  onClick={() => handleTemplateClick(template.json)}
                  disabled={saving}
                >
                  {template.name} Template
                </Button>
              ))}
            </div>
            <Button
              onClick={handleSubmit}
              disabled={isSaveDisabled()}
            >
              {saving ? "Saving..." : "Save Persona"}
            </Button>
          </CardFooter>
        </Card>
      </div>
    </div>
  )
}